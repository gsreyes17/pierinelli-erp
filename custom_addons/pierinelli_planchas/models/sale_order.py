# -*- coding: utf-8 -*-
"""
Reserva de plancha desde el pedido de venta (Plan V2, Fase 3 tareas 14 y 17).

El vendedor elige LA plancha concreta en la linea de cotizacion. Al confirmar:
- la plancha queda reservada comercialmente (cliente + asesor + 7 dias),
- la reserva de stock se fuerza a ese lote (no a cualquiera),
- y si otro vendedor ya la tenia reservada, el sistema lo bloquea con un
  mensaje claro (el problema del ERP anterior: dos vendedores agarrando la
  misma plancha).
Al contabilizar la factura, el comprobante y su fecha quedan escritos en la
ficha de cada plancha vendida.
"""
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from .stock_lot import DIAS_RESERVA


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    plancha_id = fields.Many2one(
        'stock.lot', string='Plancha',
        domain="[('product_id', '=', product_id),"
               " ('m2_disponible', '>', 0)]",
        help='Plancha concreta que se aparta para este cliente. Vacio = '
             'el sistema elige cualquiera al entregar.')
    plancha_m2 = fields.Float(
        related='plancha_id.m2_disponible', string='m² de la plancha')

    @api.onchange('plancha_id')
    def _onchange_plancha_id(self):
        """Al elegir plancha se propone vender sus m² disponibles."""
        if self.plancha_id:
            self.product_uom_qty = self.plancha_id.m2_disponible

    def _plancha_warehouse(self):
        """Almacen donde esta fisicamente la plancha (via su ubicacion)."""
        self.ensure_one()
        location = self.plancha_id.location_id
        return location.warehouse_id if location else False

    def _forzar_reserva_plancha(self):
        """Reemplaza la reserva automatica del picking por la plancha elegida."""
        for line in self:
            plancha = line.plancha_id
            moves = line.move_ids.filtered(
                lambda m: m.state not in ('done', 'cancel'))
            for move in moves:
                quant = plancha.quant_ids.filtered(
                    lambda q: q.location_id.usage == 'internal'
                    and q.quantity > 0)[:1]
                if not quant:
                    continue
                move.move_line_ids.unlink()
                move.move_line_ids = [(0, 0, {
                    'product_id': move.product_id.id,
                    'lot_id': plancha.id,
                    'quantity': min(move.product_uom_qty,
                                    plancha.m2_disponible),
                    'location_id': quant.location_id.id,
                    'location_dest_id': move.location_dest_id.id,
                })]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    orden_corte_ids = fields.One2many(
        'pierinelli.orden.corte', 'sale_order_id',
        string='Ordenes de corte')
    orden_corte_count = fields.Integer(
        compute='_compute_orden_corte_count')

    def _compute_orden_corte_count(self):
        for order in self:
            order.orden_corte_count = len(order.orden_corte_ids)

    def action_ver_ordenes_corte(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'pierinelli_planchas.action_orden_corte')
        action['domain'] = [('sale_order_id', '=', self.id)]
        action['context'] = {'default_sale_order_id': self.id}
        return action

    def action_crear_orden_corte(self):
        """Crea la Orden de Corte precargada desde el pedido: plancha de la
        primera linea que tenga una apartada, cliente y asesor."""
        self.ensure_one()
        linea = self.order_line.filtered('plancha_id')[:1]
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pierinelli.orden.corte',
            'view_mode': 'form',
            'context': {
                'default_sale_order_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_asesor_id': (self.user_id.id
                                      or self.env.user.id),
                'default_plancha_id': linea.plancha_id.id or False,
            },
        }

    def action_confirm(self):
        lineas_con_plancha = self.order_line.filtered('plancha_id')
        # Validaciones ANTES de confirmar (si algo falla, no se crea nada)
        for line in lineas_con_plancha:
            plancha = line.plancha_id
            if plancha.m2_disponible <= 0:
                raise UserError(_(
                    'La plancha %s ya no tiene stock disponible. '
                    'Elige otra.') % plancha.name)
            if (plancha.cliente_reserva_id
                    and plancha.cliente_reserva_id != line.order_id.partner_id
                    and (not plancha.reserva_fin
                         or plancha.reserva_fin >= fields.Date.context_today(self))):
                raise UserError(_(
                    'La plancha %(plancha)s ya esta reservada para '
                    '%(cliente)s (asesor: %(asesor)s, hasta %(fin)s). '
                    'Elige otra plancha o coordina con el asesor.',
                    plancha=plancha.name,
                    cliente=plancha.cliente_reserva_id.display_name,
                    asesor=plancha.asesor_id.name or '-',
                    fin=plancha.reserva_fin or '-'))
            wh_plancha = line._plancha_warehouse()
            if wh_plancha and wh_plancha != line.order_id.warehouse_id:
                raise UserError(_(
                    'La plancha %(plancha)s esta en %(sede)s pero el pedido '
                    'sale de %(pedido)s. Cambia el almacen del pedido o '
                    'traslada la plancha primero.',
                    plancha=plancha.name,
                    sede=wh_plancha.display_name,
                    pedido=line.order_id.warehouse_id.display_name))

        res = super().action_confirm()

        hoy = fields.Date.context_today(self)
        for line in lineas_con_plancha:
            plancha = line.plancha_id
            # 1) Reserva comercial en la ficha de la plancha (trazabilidad)
            plancha.write({
                'cliente_reserva_id': line.order_id.partner_id.id,
                'asesor_id': (line.order_id.user_id.id
                              or self.env.user.id),
                'reserva_inicio': hoy,
                'reserva_fin': hoy + timedelta(days=DIAS_RESERVA),
            })
            plancha.message_post(body=_(
                'Apartada por el pedido %(pedido)s para %(cliente)s '
                '(asesor: %(asesor)s).',
                pedido=line.order_id.name,
                cliente=line.order_id.partner_id.display_name,
                asesor=line.order_id.user_id.name or self.env.user.name))
            # 2) Forzar la reserva de stock a ESTA plancha (no a cualquiera)
            line._forzar_reserva_plancha()
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    orden_corte_count = fields.Integer(
        compute='_compute_orden_corte_count',
        string='Ordenes de corte')

    def _compute_orden_corte_count(self):
        for move in self:
            ordenes = move.invoice_line_ids.sale_line_ids.order_id\
                .orden_corte_ids if move.move_type == 'out_invoice' \
                else self.env['pierinelli.orden.corte']
            move.orden_corte_count = len(ordenes)

    def action_ver_ordenes_corte(self):
        """Desde la factura, ver las ordenes de corte de sus pedidos."""
        self.ensure_one()
        ordenes = self.invoice_line_ids.sale_line_ids.order_id.orden_corte_ids
        action = self.env['ir.actions.act_window']._for_xml_id(
            'pierinelli_planchas.action_orden_corte')
        action['domain'] = [('id', 'in', ordenes.ids)]
        return action

    def action_post(self):
        """Al contabilizar la factura, el comprobante queda en cada plancha."""
        res = super().action_post()
        for move in self.filtered(lambda m: m.move_type == 'out_invoice'):
            planchas = move.invoice_line_ids.sale_line_ids.plancha_id
            for plancha in planchas:
                plancha.write({
                    'comprobante': move.name,
                    'fecha_comprobante': move.invoice_date or move.date,
                })
                plancha.message_post(body=_(
                    'Facturada en %(comp)s (%(fecha)s).',
                    comp=move.name,
                    fecha=move.invoice_date or move.date))
        return res
