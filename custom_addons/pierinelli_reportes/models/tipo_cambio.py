# -*- coding: utf-8 -*-
"""
Tipos de cambio configurables (Plan V2, Fase 5 tarea 24).

Criterio del cliente: el vendedor ELIGE que tasa aplicar en cada operacion
(SUNAT o la corporativa propia) y el sistema registra cual se uso y donde.

- Catalogo de tasas por fecha y origen (SUNAT / Corporativa), administrable
  desde Contabilidad -> Tipos de Cambio.
- En la factura en moneda extranjera, el campo "Origen de la tasa" aplica la
  tasa elegida y queda registrado (con seguimiento en el chatter).

Nota tecnica: invoice_currency_rate de Odoo es "moneda extranjera por 1 sol"
(PEN -> USD), asi que se aplica 1/tasa cuando la tasa viene en S/ por USD.
"""
import re
import logging
from datetime import datetime

import requests
from lxml import html

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError


_logger = logging.getLogger(__name__)


class TipoCambio(models.Model):
    _name = 'pierinelli.tipo.cambio'
    _description = 'Tipo de cambio (SUNAT / Corporativa)'
    _order = 'fecha desc, origen'
    _rec_name = 'display_name'

    fecha = fields.Date(required=True, default=fields.Date.context_today,
                        index=True)
    origen = fields.Selection(
        [('sunat', 'SUNAT'), ('corporativa', 'Corporativa')],
        required=True, default='sunat')
    compra = fields.Float('Compra (S/ por USD)', digits=(12, 4))
    venta = fields.Float('Venta (S/ por USD)', digits=(12, 4), required=True)
    notas = fields.Char('Notas')
    actualizado_automaticamente = fields.Boolean(
        'Actualizado desde SUNAT', readonly=True, copy=False)
    fecha_actualizacion = fields.Datetime('Última consulta SUNAT', readonly=True,
                                          copy=False)

    SUNAT_URL = 'https://e-consulta.sunat.gob.pe/cl-at-ittipcam/tcS01Alias'

    _fecha_origen_unico = models.Constraint(
        'unique(fecha, origen)',
        'Ya existe una tasa de ese origen para esa fecha.',
    )

    @api.depends('fecha', 'origen', 'venta')
    def _compute_display_name(self):
        for tc in self:
            tc.display_name = '%s %s (V %.4f)' % (
                dict(tc._fields['origen'].selection).get(tc.origen, ''),
                tc.fecha or '', tc.venta or 0)

    @api.model
    def tasa_vigente(self, origen, fecha=None, lado='venta'):
        """Ultima tasa del origen dado a la fecha (o anterior mas cercana)."""
        fecha = fecha or fields.Date.context_today(self)
        tc = self.search([('origen', '=', origen), ('fecha', '<=', fecha)],
                         limit=1)
        if not tc:
            return 0.0
        return tc.venta if lado == 'venta' else (tc.compra or tc.venta)

    @api.model
    def _parse_sunat_html(self, content):
        """Obtiene la última fila de cotización publicada por SUNAT.

        SUNAT publica la tasa en una página de consulta, no en una API REST
        versionada. El parser es deliberadamente conservador: acepta solamente
        una fecha dd/mm/aaaa seguida de dos valores numéricos (compra/venta).
        Si la estructura cambia, no escribe una tasa potencialmente errónea.
        """
        try:
            document = html.fromstring(content)
        except (TypeError, ValueError) as error:
            raise UserError(_('SUNAT devolvió una respuesta no válida: %s') % error)

        date_pattern = re.compile(r'\b(\d{2}/\d{2}/\d{4})\b')
        number_pattern = re.compile(r'^\d+(?:[,.]\d+)?$')
        candidates = []
        for row in document.xpath('//tr'):
            values = [' '.join(cell.itertext()).strip()
                      for cell in row.xpath('./th|./td')]
            date_match = next((date_pattern.search(value) for value in values
                               if date_pattern.search(value)), None)
            numbers = [value.replace(',', '.') for value in values
                       if number_pattern.match(value.replace(' ', ''))]
            if date_match and len(numbers) >= 2:
                try:
                    candidates.append((datetime.strptime(
                        date_match.group(1), '%d/%m/%Y').date(), float(numbers[-2]),
                        float(numbers[-1])))
                except ValueError:
                    continue
        if not candidates:
            raise UserError(_(
                'No fue posible identificar compra y venta en la respuesta de '
                'SUNAT. Registra la tasa manualmente y revisa la conexión.'))
        return max(candidates, key=lambda value: value[0])

    @api.model
    def _obtener_tasa_sunat(self):
        try:
            response = requests.get(
                self.SUNAT_URL, timeout=25,
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; PierinelliERP/1.0)',
                    'Accept': 'text/html,application/xhtml+xml',
                    'Accept-Language': 'es-PE,es;q=0.9',
                })
            response.raise_for_status()
        except requests.RequestException as error:
            raise UserError(_(
                'No se pudo consultar SUNAT. Puedes registrar la tasa '
                'manualmente y volver a intentar más tarde. Detalle: %s') % error)
        return self._parse_sunat_html(response.content)

    @api.model
    def actualizar_desde_sunat(self):
        if not (self.env.user.has_group('account.group_account_manager')
                or self.env.user.has_group('base.group_system')):
            raise AccessError(_(
                'Solo un responsable contable o Administrador puede actualizar '
                'la tasa desde SUNAT.'))
        fecha, compra, venta = self._obtener_tasa_sunat()
        values = {
            'compra': compra,
            'venta': venta,
            'actualizado_automaticamente': True,
            'fecha_actualizacion': fields.Datetime.now(),
            'notas': 'Consulta automática desde SUNAT',
        }
        rate = self.search([('fecha', '=', fecha), ('origen', '=', 'sunat')],
                           limit=1)
        if rate and not rate.actualizado_automaticamente:
            return rate, False
        if rate:
            rate.write(values)
        else:
            rate = self.create(dict(values, fecha=fecha, origen='sunat'))
        return rate, True

    @api.model
    def _cron_actualizar_sunat(self):
        """Entrada del cron. Se activa manualmente tras una primera prueba."""
        try:
            self.sudo().actualizar_desde_sunat()
        except UserError as error:
            # El cron no invalida los documentos ni borra la última tasa válida;
            # deja el detalle técnico en el log para que el contador decida.
            _logger.warning('No se actualizó el tipo de cambio SUNAT: %s', error)


class TipoCambioActualizar(models.TransientModel):
    _name = 'pierinelli.tipo.cambio.actualizar'
    _description = 'Actualizar tipo de cambio SUNAT'

    def action_actualizar(self):
        rate, updated = self.env['pierinelli.tipo.cambio'].actualizar_desde_sunat()
        message = (_('Tasa SUNAT registrada: %(date)s · compra %(buy).4f · '
                     'venta %(sell).4f.') if updated else _(
            'Ya existe una tasa SUNAT ingresada manualmente para %(date)s; '
            'el sistema la conservó.')) % {
                'date': rate.fecha, 'buy': rate.compra, 'sell': rate.venta}
        return {
            'type': 'ir.actions.client', 'tag': 'display_notification',
            'params': {'title': _('Tipo de cambio SUNAT'), 'message': message,
                       'type': 'success' if updated else 'warning',
                       'sticky': False},
        }


class AccountMove(models.Model):
    _inherit = 'account.move'

    origen_tasa = fields.Selection(
        [('sunat_venta', 'SUNAT venta'),
         ('sunat_compra', 'SUNAT compra'),
         ('corporativa', 'Corporativa'),
         ('manual', 'Manual')],
        string='Origen de la tasa', tracking=True, copy=False,
        help='Que tipo de cambio se aplico en este documento. El vendedor '
             'elige; queda registrado para trazabilidad.')
    tasa_aplicada = fields.Float(
        'Tasa aplicada (S/ por USD)', digits=(12, 4), copy=False,
        readonly=True, tracking=True)

    # Estado abierto/cerrado del panel de tipo de cambio en la factura.
    # Calculado y NO almacenado: al elegir un origen la dependencia cambia, el
    # compute se reevalua y el panel se pliega solo (readonly=False permite que
    # el usuario lo vuelva a abrir sin guardar el documento).
    mostrar_opciones_tasa = fields.Boolean(
        string='Cambiar tasa',
        compute='_compute_mostrar_opciones_tasa',
        readonly=False, store=False, copy=False,
        help='Muestra u oculta las opciones de tipo de cambio. Se pliega solo '
             'al elegir un origen.')

    # Resumen de una linea ("SUNAT venta - 3.7520 S/ por USD") para que el panel
    # plegado siga diciendo que tasa se aplico sin repetir origen_tasa en la
    # vista (un mismo campo dos veces en un form dispara warning de Odoo).
    resumen_tasa = fields.Char(compute='_compute_resumen_tasa')

    @api.depends('origen_tasa')
    def _compute_mostrar_opciones_tasa(self):
        for move in self:
            move.mostrar_opciones_tasa = not move.origen_tasa

    @api.depends('origen_tasa', 'tasa_aplicada')
    def _compute_resumen_tasa(self):
        etiquetas = dict(self._fields['origen_tasa'].selection)
        for move in self:
            if move.origen_tasa and move.tasa_aplicada:
                move.resumen_tasa = '%s · %.4f S/ por USD' % (
                    etiquetas.get(move.origen_tasa, ''), move.tasa_aplicada)
            else:
                move.resumen_tasa = False

    @api.depends('origen_tasa', 'tasa_aplicada')
    def _compute_invoice_currency_rate(self):
        """La tasa ELEGIDA es la tasa del documento, pase lo que pase.

        El compute del core reasigna invoice_currency_rate desde la tabla de
        monedas de Odoo cada vez que cambia la fecha de la factura (incluida
        la que se fija sola al publicar). Sin este override, una factura que
        heredaba la tasa de la cotizacion terminaba posteada con la tasa por
        defecto (1.0 si res.currency.rate esta vacia): $177 se asentaban como
        S/ 177. Aqui la eleccion SUNAT/corporativa vuelve a imponerse tras
        cualquier recalculo; el origen 'manual' conserva el comportamiento
        estandar de Odoo."""
        super()._compute_invoice_currency_rate()
        for move in self:
            if (move.origen_tasa and move.origen_tasa != 'manual'
                    and move.tasa_aplicada
                    and move.currency_id != move.company_currency_id
                    and move.is_invoice(include_receipts=True)):
                move.invoice_currency_rate = 1.0 / move.tasa_aplicada

    @api.onchange('origen_tasa', 'invoice_date')
    def _onchange_origen_tasa(self):
        for move in self:
            if (not move.origen_tasa or move.origen_tasa == 'manual'
                    or move.currency_id == move.company_currency_id):
                continue
            origen, lado = ('sunat', 'venta')
            if move.origen_tasa == 'sunat_compra':
                lado = 'compra'
            elif move.origen_tasa == 'corporativa':
                origen = 'corporativa'
            tasa = self.env['pierinelli.tipo.cambio'].tasa_vigente(
                origen, move.invoice_date, lado)
            if not tasa:
                raise UserError(_(
                    'No hay tasa %s registrada. Cargala primero en '
                    'Contabilidad → Tipos de Cambio.') % move.origen_tasa)
            move.tasa_aplicada = tasa
            # invoice_currency_rate = moneda extranjera por 1 sol
            move.invoice_currency_rate = 1.0 / tasa
