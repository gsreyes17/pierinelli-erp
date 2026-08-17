# -*- coding: utf-8 -*-
"""
Kardex de producto: fisico y valorizado.

Pedido del contador del cliente: un kardex clasico por producto con saldo
corriente, en dos vistas:
  - FISICO: entradas / salidas / saldo en unidades (m2 para planchas).
  - VALORIZADO: ademas costo unitario, valor de entrada/salida y saldo
    valorizado (criterio promedio, consistente con AVCO).

Fuente de datos: stock.move hechos. El costo unitario de cada movimiento sale
de move.value (stock_account) cuando existe; si no, del precio del movimiento
o del costo promedio del producto — el mismo criterio del formato 13.1 del
wizard SIRE, para que ambos reportes cuenten la misma historia.

El flujo es deliberadamente simple: un solo boton "Ver kardex" arma la vista
en pantalla; Excel y PDF salen de lo ya calculado. Ademas hay un boton
"Kardex" en la ficha del producto que llega aqui con el producto puesto.
"""
import base64
import io
from datetime import timedelta
from urllib.parse import quote

from odoo import api, fields, models, _
from odoo.exceptions import UserError

try:
    import xlsxwriter
except ImportError:  # pragma: no cover
    xlsxwriter = None


class KardexProductoWizard(models.TransientModel):
    _name = 'pierinelli.kardex.producto'
    _description = 'Kardex fisico y valorizado por producto'

    product_id = fields.Many2one(
        'product.product', string='Producto', required=True,
        domain=[('is_storable', '=', True)])
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Almacen',
        help='Vacio = toda la empresa. Con almacen elegido, un traslado a '
             'otra sede cuenta como salida (y viceversa).')
    date_from = fields.Date(
        'Desde', required=True,
        default=lambda self: fields.Date.context_today(self).replace(
            month=1, day=1))
    date_to = fields.Date(
        'Hasta', required=True, default=fields.Date.context_today)
    modo = fields.Selection(
        [('fisico', 'Kardex fisico (unidades)'),
         ('valorizado', 'Kardex valorizado (unidades + costo)')],
        required=True, default='valorizado')

    line_ids = fields.One2many(
        'pierinelli.kardex.producto.linea', 'wizard_id', readonly=True)
    preparado = fields.Boolean(readonly=True)

    saldo_inicial_qty = fields.Float('Saldo inicial', digits=(12, 2),
                                     readonly=True)
    saldo_inicial_valor = fields.Float('Valor inicial (S/)', digits=(12, 2),
                                       readonly=True)
    total_entrada_qty = fields.Float('Entradas', digits=(12, 2), readonly=True)
    total_entrada_valor = fields.Float('Valor entradas (S/)', digits=(12, 2),
                                       readonly=True)
    total_salida_qty = fields.Float('Salidas', digits=(12, 2), readonly=True)
    total_salida_valor = fields.Float('Valor salidas (S/)', digits=(12, 2),
                                      readonly=True)
    saldo_final_qty = fields.Float('Saldo final', digits=(12, 2),
                                   readonly=True)
    saldo_final_valor = fields.Float('Valor final (S/)', digits=(12, 2),
                                     readonly=True)

    export_file = fields.Binary(readonly=True, attachment=False)
    export_filename = fields.Char(readonly=True)

    # ------------------------------------------------------------------
    #  Clasificacion de cada movimiento respecto al ambito elegido
    # ------------------------------------------------------------------
    def _ubicacion_es_propia(self, location):
        """Interna y, si hay almacen elegido, de ESE almacen."""
        if location.usage != 'internal':
            return False
        if self.warehouse_id and location.warehouse_id != self.warehouse_id:
            return False
        return True

    def _clasificar(self, move):
        """'entrada' / 'salida' / 'traslado' / None (no afecta el ambito)."""
        origen = self._ubicacion_es_propia(move.location_id)
        destino = self._ubicacion_es_propia(move.location_dest_id)
        if destino and not origen:
            return 'entrada'
        if origen and not destino:
            return 'salida'
        if origen and destino:
            return 'traslado'
        return None

    def _costo_unitario(self, move, qty):
        """Costo por unidad del movimiento, criterio del formato 13.1."""
        valor = abs(getattr(move, 'value', 0.0) or 0.0)
        if valor and qty:
            return valor / qty
        return abs(move.price_unit or 0.0) or self.product_id.standard_price

    def _moves(self, hasta_exclusivo=None, desde=None):
        domain = [
            ('state', '=', 'done'),
            ('product_id', '=', self.product_id.id),
        ]
        if desde:
            domain.append(('date', '>=', fields.Datetime.to_datetime(desde)))
        if hasta_exclusivo:
            domain.append(
                ('date', '<', fields.Datetime.to_datetime(hasta_exclusivo)))
        return self.env['stock.move'].sudo().search(
            domain, order='date, id')

    # ------------------------------------------------------------------
    #  Armado del kardex
    # ------------------------------------------------------------------
    def _ajuste_carga_directa(self):
        """Stock cargado SIN movimiento (quants directos).

        El alta masiva de planchas y la apertura del seed escriben quants
        directamente (Quant._update_available_quantity), sin generar
        stock.move. Un kardex basado solo en movimientos no los ve y termina
        en saldos negativos absurdos. La diferencia entre el stock fisico
        real y el neto de TODOS los movimientos es exactamente esa carga
        directa; se incorpora al saldo inicial, valorizada al costo promedio
        del producto (la unica valorizacion disponible para algo que no tiene
        documento).
        """
        quants = self.env['stock.quant'].sudo().search([
            ('product_id', '=', self.product_id.id),
            ('location_id.usage', '=', 'internal'),
        ])
        if self.warehouse_id:
            quants = quants.filtered(
                lambda q: q.location_id.warehouse_id == self.warehouse_id)
        qty_real = sum(quants.mapped('quantity'))

        neto_moves = 0.0
        for move in self._moves():
            tipo = self._clasificar(move)
            if tipo == 'entrada':
                neto_moves += move.quantity
            elif tipo == 'salida':
                neto_moves -= move.quantity
        return qty_real - neto_moves

    def action_preparar(self):
        self.ensure_one()
        if self.date_from > self.date_to:
            raise UserError(_('La fecha "Desde" no puede ser posterior a '
                              '"Hasta".'))
        self.line_ids.unlink()

        # Punto de partida: la carga directa (sin documento) valorizada al
        # promedio, y encima todo lo movido antes del rango.
        ajuste = self._ajuste_carga_directa()
        qty_ini = ajuste
        valor_ini = ajuste * (self.product_id.standard_price or 0.0)
        for move in self._moves(hasta_exclusivo=self.date_from):
            tipo = self._clasificar(move)
            if tipo == 'entrada':
                qty_ini += move.quantity
                valor_ini += move.quantity * self._costo_unitario(
                    move, move.quantity)
            elif tipo == 'salida':
                costo = (valor_ini / qty_ini) if qty_ini else \
                    self._costo_unitario(move, move.quantity)
                qty_ini -= move.quantity
                valor_ini -= move.quantity * costo

        saldo_qty, saldo_valor = qty_ini, valor_ini
        tot_ent_q = tot_ent_v = tot_sal_q = tot_sal_v = 0.0
        lineas = []
        for move in self._moves(desde=self.date_from,
                                hasta_exclusivo=self.date_to
                                + timedelta(days=1)):
            tipo = self._clasificar(move)
            if tipo is None:
                continue
            qty = move.quantity
            ent_q = sal_q = ent_v = sal_v = 0.0
            if tipo == 'entrada':
                costo = self._costo_unitario(move, qty)
                ent_q, ent_v = qty, qty * costo
                saldo_qty += qty
                saldo_valor += ent_v
                tot_ent_q += ent_q
                tot_ent_v += ent_v
            elif tipo == 'salida':
                # La salida se valoriza al PROMEDIO del saldo (kardex AVCO),
                # no al precio del movimiento.
                costo = (saldo_valor / saldo_qty) if saldo_qty else \
                    self._costo_unitario(move, qty)
                sal_q, sal_v = qty, qty * costo
                saldo_qty -= qty
                saldo_valor -= sal_v
                tot_sal_q += sal_q
                tot_sal_v += sal_v
            else:  # traslado dentro del ambito: no cambia el saldo
                costo = (saldo_valor / saldo_qty) if saldo_qty else 0.0
            lotes = ', '.join(move.lot_ids.mapped('name')[:3])
            if len(move.lot_ids) > 3:
                lotes += ' (+%d)' % (len(move.lot_ids) - 3)
            lineas.append((0, 0, {
                'fecha': fields.Datetime.to_datetime(move.date).date(),
                'documento': move.reference or move.picking_id.name or '',
                'tipo': tipo,
                'detalle': '%s → %s' % (move.location_id.complete_name,
                                        move.location_dest_id.complete_name),
                'lotes': lotes,
                'entrada_qty': ent_q,
                'salida_qty': sal_q,
                'saldo_qty': saldo_qty,
                'costo_unitario': costo,
                'entrada_valor': ent_v,
                'salida_valor': sal_v,
                'saldo_valor': saldo_valor,
            }))

        self.write({
            'line_ids': lineas,
            'preparado': True,
            'saldo_inicial_qty': qty_ini,
            'saldo_inicial_valor': valor_ini,
            'total_entrada_qty': tot_ent_q,
            'total_entrada_valor': tot_ent_v,
            'total_salida_qty': tot_sal_q,
            'total_salida_valor': tot_sal_v,
            'saldo_final_qty': saldo_qty,
            'saldo_final_valor': saldo_valor,
            'export_file': False,
            'export_filename': False,
        })
        return self._reabrir()

    def _reabrir(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _ensure_prepared(self):
        if not self.preparado:
            raise UserError(_('Primero pulsa "Ver kardex".'))

    # ------------------------------------------------------------------
    #  Exportaciones
    # ------------------------------------------------------------------
    def action_export_xlsx(self):
        self._ensure_prepared()
        if xlsxwriter is None:
            raise UserError(_('No esta instalada la libreria xlsxwriter.'))
        valorizado = self.modo == 'valorizado'
        stream = io.BytesIO()
        wb = xlsxwriter.Workbook(stream, {'in_memory': True})
        ws = wb.add_worksheet('Kardex')
        titulo = wb.add_format({'bold': True, 'font_size': 15,
                                'font_color': '#FFFFFF',
                                'bg_color': '#111111'})
        oro = wb.add_format({'bold': True, 'bg_color': '#C9962F',
                             'border': 1})
        cab = wb.add_format({'bold': True, 'font_color': '#FFFFFF',
                             'bg_color': '#111111', 'border': 1,
                             'align': 'center', 'text_wrap': True})
        txt = wb.add_format({'border': 1})
        fec = wb.add_format({'border': 1, 'num_format': 'dd/mm/yyyy'})
        num = wb.add_format({'border': 1, 'num_format': '#,##0.00'})

        headers = ['Fecha', 'Documento', 'Tipo', 'Detalle', 'Lotes/Planchas',
                   'Entrada', 'Salida', 'Saldo']
        if valorizado:
            headers += ['Costo unit. (S/)', 'Valor entrada (S/)',
                        'Valor salida (S/)', 'Saldo valorizado (S/)']
        ws.merge_range(0, 0, 0, len(headers) - 1,
                       'Kardex %s — %s' % (
                           'valorizado' if valorizado else 'fisico',
                           self.product_id.display_name), titulo)
        ws.write(1, 0, 'Empresa', oro)
        ws.write(1, 1, self.env.company.display_name)
        ws.write(1, 3, 'Almacen', oro)
        ws.write(1, 4, self.warehouse_id.name or 'Todos')
        ws.write(1, 5, 'Periodo', oro)
        ws.write(1, 6, '%s al %s' % (self.date_from.strftime('%d/%m/%Y'),
                                     self.date_to.strftime('%d/%m/%Y')))
        ws.write(2, 0, 'Saldo inicial', oro)
        ws.write_number(2, 1, self.saldo_inicial_qty, num)
        if valorizado:
            ws.write(2, 3, 'Valor inicial S/', oro)
            ws.write_number(2, 4, self.saldo_inicial_valor, num)
        for col, h in enumerate(headers):
            ws.write(4, col, h, cab)
        fila = 5
        for ln in self.line_ids:
            valores = [
                (ln.fecha, fec), (ln.documento, txt),
                (dict(ln._fields['tipo'].selection).get(ln.tipo), txt),
                (ln.detalle, txt), (ln.lotes, txt),
                (ln.entrada_qty, num), (ln.salida_qty, num),
                (ln.saldo_qty, num)]
            if valorizado:
                valores += [(ln.costo_unitario, num), (ln.entrada_valor, num),
                            (ln.salida_valor, num), (ln.saldo_valor, num)]
            for col, (valor, formato) in enumerate(valores):
                if formato is fec and valor:
                    ws.write_datetime(fila, col, fields.Datetime.to_datetime(
                        valor), fec)
                elif formato is num:
                    ws.write_number(fila, col, valor or 0.0, num)
                else:
                    ws.write(fila, col, valor or '', formato)
            fila += 1
        ws.write(fila, 4, 'TOTALES', oro)
        ws.write_number(fila, 5, self.total_entrada_qty, num)
        ws.write_number(fila, 6, self.total_salida_qty, num)
        ws.write_number(fila, 7, self.saldo_final_qty, num)
        if valorizado:
            ws.write_number(fila, 9, self.total_entrada_valor, num)
            ws.write_number(fila, 10, self.total_salida_valor, num)
            ws.write_number(fila, 11, self.saldo_final_valor, num)
        anchos = [11, 18, 10, 42, 24, 10, 10, 10, 13, 14, 14, 16]
        for col, ancho in enumerate(anchos[:len(headers)]):
            ws.set_column(col, col, ancho)
        wb.close()
        self.write({
            'export_file': base64.b64encode(stream.getvalue()),
            'export_filename': 'kardex_%s_%s.xlsx' % (
                self.modo, (self.product_id.default_code or 'producto')),
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=%s&id=%s&field=export_file'
                   '&filename_field=export_filename&download=true&filename=%s'
                   % (self._name, self.id, quote(self.export_filename)),
            'target': 'self',
        }

    def action_export_pdf(self):
        self._ensure_prepared()
        return self.env.ref(
            'pierinelli_almacenes.action_report_kardex_producto'
        ).report_action(self)


class KardexProductoLinea(models.TransientModel):
    _name = 'pierinelli.kardex.producto.linea'
    _description = 'Linea de kardex de producto'
    _order = 'fecha, id'

    wizard_id = fields.Many2one('pierinelli.kardex.producto', required=True,
                                ondelete='cascade')
    fecha = fields.Date(readonly=True)
    documento = fields.Char(readonly=True)
    tipo = fields.Selection(
        [('entrada', 'Entrada'), ('salida', 'Salida'),
         ('traslado', 'Traslado')], readonly=True)
    detalle = fields.Char('Origen → destino', readonly=True)
    lotes = fields.Char('Lotes / planchas', readonly=True)
    entrada_qty = fields.Float('Entrada', digits=(12, 2), readonly=True)
    salida_qty = fields.Float('Salida', digits=(12, 2), readonly=True)
    saldo_qty = fields.Float('Saldo', digits=(12, 2), readonly=True)
    costo_unitario = fields.Float('Costo unit. (S/)', digits=(12, 4),
                                  readonly=True)
    entrada_valor = fields.Float('Valor entrada (S/)', digits=(12, 2),
                                 readonly=True)
    salida_valor = fields.Float('Valor salida (S/)', digits=(12, 2),
                                readonly=True)
    saldo_valor = fields.Float('Saldo valorizado (S/)', digits=(12, 2),
                               readonly=True)


class ProductTemplateKardex(models.Model):
    _inherit = 'product.template'

    def action_abrir_kardex(self):
        """Boton "Kardex" en la ficha del producto: llega con todo puesto."""
        self.ensure_one()
        wizard = self.env['pierinelli.kardex.producto'].create({
            'product_id': self.product_variant_id.id,
        })
        wizard.action_preparar()
        return wizard._reabrir()
