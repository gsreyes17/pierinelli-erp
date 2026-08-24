# -*- coding: utf-8 -*-
"""La obra (cuenta analitica) como centro de consulta: desde su ficha se
abren los pedidos, facturas y apuntes que la llevan en su distribucion."""
from odoo import _, api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    pedidos_count = fields.Integer(compute='_compute_documentos')
    facturas_count = fields.Integer(compute='_compute_documentos')

    def _compute_documentos(self):
        SO = self.env['sale.order']
        AM = self.env['account.move']
        for cuenta in self:
            cuenta.pedidos_count = SO.search_count([
                ('order_line.analytic_distribution', 'in', cuenta.ids)])
            cuenta.facturas_count = AM.search_count([
                ('move_type', 'in', ('out_invoice', 'out_refund',
                                     'in_invoice', 'in_refund')),
                ('line_ids.analytic_distribution', 'in', cuenta.ids)])

    def action_ver_pedidos(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pedidos de %s') % self.name,
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('order_line.analytic_distribution', 'in', self.ids)],
        }

    def action_ver_facturas(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Facturas de %s') % self.name,
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('move_type', 'in', ('out_invoice', 'out_refund',
                                            'in_invoice', 'in_refund')),
                       ('line_ids.analytic_distribution', 'in', self.ids)],
        }
