# -*- coding: utf-8 -*-
"""
Registro manual de merma (rotura, defecto, muestra) fuera de un corte.
La cantidad sale del stock vendible a la Zona de Mermas y queda su registro
con motivo, destino y valor.
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError

from ..models.orden_corte import MOTIVOS_MERMA, get_location_mermas


class RegistrarMerma(models.TransientModel):
    _name = 'pierinelli.registrar.merma'
    _description = 'Registrar merma manual'

    plancha_id = fields.Many2one(
        'stock.lot', string='Plancha', required=True,
        domain=[('m2_disponible', '>', 0)])
    m2_disponible = fields.Float(
        related='plancha_id.m2_disponible', string='m² disponibles')
    m2 = fields.Float('m² de merma', digits=(8, 2), required=True)
    motivo = fields.Selection(MOTIVOS_MERMA, required=True, default='rotura')
    destino = fields.Selection(
        [('cliente', 'Asumida por el cliente'),
         ('negocio', 'Perdida del negocio')],
        required=True, default='negocio')
    notas = fields.Char('Notas')

    @api.onchange('plancha_id')
    def _onchange_plancha(self):
        if self.plancha_id and not self.m2:
            self.m2 = self.plancha_id.m2_disponible

    def action_registrar(self):
        self.ensure_one()
        if self.m2 <= 0:
            raise UserError(_('Los m² de merma deben ser mayores a cero.'))
        if self.m2 > self.plancha_id.m2_disponible + 0.01:
            raise UserError(_(
                'La plancha %(p)s solo tiene %(d).2f m² disponibles.',
                p=self.plancha_id.name, d=self.plancha_id.m2_disponible))
        quant = self.plancha_id.quant_ids.filtered(
            lambda q: q.location_id.usage == 'internal' and q.quantity > 0)[:1]
        if not quant:
            raise UserError(_('La plancha no tiene stock interno.'))

        Quant = self.env['stock.quant']
        loc_mermas = get_location_mermas(self.env)
        Quant._update_available_quantity(
            self.plancha_id.product_id, quant.location_id, -self.m2,
            lot_id=self.plancha_id)
        Quant._update_available_quantity(
            self.plancha_id.product_id, loc_mermas, self.m2,
            lot_id=self.plancha_id)
        merma = self.env['pierinelli.merma'].create({
            'plancha_id': self.plancha_id.id,
            'm2': self.m2,
            'motivo': self.motivo,
            'destino': self.destino,
            'notas': self.notas,
            'warehouse_id': (quant.location_id.warehouse_id.id
                             if quant.location_id.warehouse_id else False),
        })
        self.plancha_id.message_post(body=_(
            'Merma registrada: %(m2).2f m² (%(motivo)s, %(destino)s).',
            m2=self.m2,
            motivo=dict(MOTIVOS_MERMA)[self.motivo],
            destino=dict(merma._fields['destino'].selection)[self.destino]))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pierinelli.merma',
            'view_mode': 'list',
            'domain': [('id', '=', merma.id)],
        }
