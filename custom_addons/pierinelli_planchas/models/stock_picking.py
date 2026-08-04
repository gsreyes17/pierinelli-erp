# -*- coding: utf-8 -*-
"""Integra la recepcion de compras con el alta individual de planchas."""
from odoo import _, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_registrar_planchas_recepcion(self):
        self.ensure_one()
        if self.picking_type_code != 'incoming':
            raise UserError(_('El registro de planchas solo aplica a recepciones.'))
        if self.state in ('done', 'cancel'):
            raise UserError(_('Esta recepcion ya no puede modificarse.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Registrar planchas recibidas'),
            'res_model': 'pierinelli.recepcion.planchas',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_picking_id': self.id},
        }

    def _action_done(self):
        """Una recepcion de productos por lote no puede validarse sin lotes.

        Esto evita el atajo que antes permitia recibir m2 agregados y luego
        volver a ingresarlos con el asistente de alta masiva.
        """
        for picking in self.filtered(lambda p: p.picking_type_code == 'incoming'):
            tracked = picking.move_ids.filtered(
                lambda m: m.product_id.tracking == 'lot' and m.quantity > 0)
            missing = tracked.filtered(lambda m: not m.move_line_ids.filtered('lot_id'))
            if missing:
                raise UserError(_(
                    'Registra las planchas antes de validar la recepcion. '
                    'Usa el boton "Registrar planchas recibidas" en %s.')
                    % picking.name)
        return super()._action_done()
