# -*- coding: utf-8 -*-
"""Trazabilidad del reingreso de mermas."""
from odoo import fields, models, _
from odoo.exceptions import UserError

from .orden_corte import get_location_mermas


class Merma(models.Model):
    _inherit = 'pierinelli.merma'

    def action_reingresar(self):
        """Recupera la merma en una nueva plancha hija, nunca en el lote origen."""
        Quant = self.env['stock.quant']
        loc_mermas = get_location_mermas(self.env)
        for merma in self:
            if merma.destino == 'reingreso' or merma.plancha_reingreso_id:
                raise UserError(_('Esta merma ya fue reingresada.'))
            destino = (merma.warehouse_id.lot_stock_id
                       if merma.warehouse_id
                       else self.env['stock.warehouse'].search([], limit=1)
                       .lot_stock_id)
            if not destino:
                raise UserError(_('No se encontro una ubicacion de stock para '
                                  'reingresar la merma.'))
            origen = merma.plancha_id
            reingreso = self.env['stock.lot'].create({
                'name': origen.siguiente_codigo_corte(),
                'product_id': origen.product_id.id,
                'company_id': origen.company_id.id,
                # La merma tiene area, pero no dimensiones fisicas fiables.
                'm2_neto': merma.m2,
                'espesor': origen.espesor,
                'condicion': origen.condicion,
                'aptitud_comercial': 'pendiente',
                'modo_venta': origen.modo_venta,
                'ubicacion_ref': origen.ubicacion_ref,
                'ref_importacion': origen.ref_importacion,
                'fecha_ingreso': fields.Date.context_today(self),
                'plancha_madre_id': origen.id,
                'image_1920': origen.image_1920 or False,
                'observaciones': _('Reingreso de merma. Medir largo y alto '
                                   'antes de habilitarla para venta.'),
            })
            Quant._update_available_quantity(
                origen.product_id, loc_mermas, -merma.m2, lot_id=origen)
            Quant._update_available_quantity(
                origen.product_id, destino, merma.m2, lot_id=reingreso)
            merma.write({
                'destino': 'reingreso',
                'plancha_reingreso_id': reingreso.id,
            })
            origen.message_post(body=_(
                'Merma de %(m2).2f m2 recuperada como la plancha %(nueva)s '
                'en %(sede)s.', m2=merma.m2, nueva=reingreso.name,
                sede=destino.display_name))
            reingreso.message_post(body=_(
                'Creada al reingresar la merma de %(origen)s (%(m2).2f m2). '
                'Complete sus medidas y revise su aptitud comercial.',
                origen=origen.name, m2=merma.m2))
