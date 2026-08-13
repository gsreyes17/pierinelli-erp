from odoo import api, models


class PanelContable(models.AbstractModel):
    _name = 'pierinelli.panel.contable'
    _description = 'Panel contable'

    @api.model
    def get_data(self):
        Move = self.env['account.move']
        return {
            'borradores': Move.search_count([('state', '=', 'draft'), ('move_type', '=', 'entry')]),
            'por_cobrar': Move.search_count([('move_type', '=', 'out_invoice'), ('payment_state', 'in', ('not_paid', 'partial'))]),
            'por_pagar': Move.search_count([('move_type', '=', 'in_invoice'), ('payment_state', 'in', ('not_paid', 'partial'))]),
            'cajas_abiertas': self.env['pierinelli.caja.chica'].search_count([('state', '=', 'abierta')]),
            'tributos_pendientes': self.env['pierinelli.control.tributario'].search_count([('estado', '=', 'pendiente')]),
            'presupuestos_abiertos': self.env['pierinelli.presupuesto.financiero'].search_count([('state', '=', 'aprobado')]),
            'arqueos_pendientes': self.env['pierinelli.arqueo.cobranza'].search_count([('state', '=', 'borrador')]),
        }
