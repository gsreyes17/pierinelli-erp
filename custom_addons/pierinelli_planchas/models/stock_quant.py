# -*- coding: utf-8 -*-
"""
Motivo obligatorio en los ajustes de inventario (Plan V2, Fase 4 tarea 21).

Odoo Community no trae campo de motivo en los ajustes: cualquier diferencia
de conteo quedaba sin explicacion. Aqui ningun ajuste se aplica sin decir
por que.
"""
from odoo import fields, models, _
from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    motivo_ajuste = fields.Char(
        'Motivo del ajuste',
        help='Obligatorio para aplicar una diferencia de inventario: '
             'rotura, conteo fisico, extravio, correccion de medida...')

    def action_apply_inventory(self):
        sin_motivo = self.filtered(
            lambda q: q.inventory_quantity_set
            and q.inventory_diff_quantity and not q.motivo_ajuste)
        if sin_motivo:
            raise UserError(_(
                'Indica el MOTIVO del ajuste antes de aplicarlo:\n- %s')
                % '\n- '.join(
                    '%s (%+.2f)' % (q.product_id.display_name,
                                    q.inventory_diff_quantity)
                    for q in sin_motivo[:10]))
        res = super().action_apply_inventory()
        # El motivo queda en el historial de movimientos como referencia
        for quant in self.filtered('motivo_ajuste'):
            moves = self.env['stock.move.line'].search([
                ('product_id', '=', quant.product_id.id),
                ('is_inventory', '=', True),
            ], order='id desc', limit=1)
            if moves and quant.motivo_ajuste not in (moves.reference or ''):
                moves.move_id.write({
                    'reference': '%s — %s' % (
                        moves.reference or 'Ajuste', quant.motivo_ajuste)})
        self.filtered('motivo_ajuste').write({'motivo_ajuste': False})
        return res
