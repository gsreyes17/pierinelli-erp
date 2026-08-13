from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    referidor_id = fields.Many2one(
        'res.partner', string='Referidor',
        help='Persona o empresa que refirio a este cliente.')
    referido_ids = fields.One2many('res.partner', 'referidor_id', string='Clientes referidos')
