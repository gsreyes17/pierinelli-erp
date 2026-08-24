# -*- coding: utf-8 -*-
"""Regla de secuencia para las lineas que requieren corte."""
from odoo import _, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _action_done(self):
        for picking in self.filtered(lambda p: p.picking_type_code == 'outgoing'):
            for move in picking.move_ids.filtered(lambda m: m.sale_line_id.requiere_corte):
                line = move.sale_line_id
                # Se busca por SECCION: en una orden multi-plancha, el
                # legado orden.plancha_id solo apunta a la primera y dejaria
                # bloqueadas las entregas de las demas planchas ya cortadas.
                orden = self.env['pierinelli.orden.corte.plancha'].search_count([
                    ('orden_id.sale_order_id', '=', line.order_id.id),
                    ('plancha_id', '=', line.plancha_id.id),
                    ('orden_id.state', '=', 'hecho'),
                ])
                if not orden:
                    raise UserError(_(
                        'La linea %s requiere corte. Ejecuta primero la Orden '
                        'de Corte de la plancha %s.')
                        % (move.product_id.display_name, line.plancha_id.name))
        return super()._action_done()
