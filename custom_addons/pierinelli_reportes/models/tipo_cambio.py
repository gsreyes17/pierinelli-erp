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
from odoo import api, fields, models, _
from odoo.exceptions import UserError


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

    _sql_constraints = [
        ('fecha_origen_unico', 'unique(fecha, origen)',
         'Ya existe una tasa de ese origen para esa fecha.'),
    ]

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
