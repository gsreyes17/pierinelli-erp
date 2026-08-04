# -*- coding: utf-8 -*-
"""Asistente para crear las planchas dentro de una recepcion de compra."""
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class RecepcionPlanchas(models.TransientModel):
    _name = 'pierinelli.recepcion.planchas'
    _description = 'Registrar planchas de una recepcion'

    picking_id = fields.Many2one('stock.picking', required=True, readonly=True)
    line_ids = fields.One2many('pierinelli.recepcion.planchas.linea', 'wizard_id', string='Planchas')

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        picking = self.env['stock.picking'].browse(self.env.context.get('default_picking_id'))
        if picking:
            lines = []
            for move in picking.move_ids.filtered(lambda m: m.state not in ('done', 'cancel')):
                if move.product_id.tracking != 'lot':
                    continue
                lines.append((0, 0, {
                    'move_id': move.id,
                    'cantidad_planchas': 1,
                    'm2_recibidos': move.product_uom_qty,
                }))
            vals['line_ids'] = lines
        return vals

    def action_registrar(self):
        self.ensure_one()
        if self.picking_id.state in ('done', 'cancel'):
            raise UserError(_('La recepcion ya no puede modificarse.'))
        by_move = {}
        for line in self.line_ids:
            if line.cantidad_planchas <= 0 or line.largo <= 0 or line.alto <= 0:
                raise ValidationError(_('Cada fila debe indicar numero de planchas, largo y alto validos.'))
            by_move.setdefault(line.move_id.id, self.env['pierinelli.recepcion.planchas.linea'])
            by_move[line.move_id.id] |= line
        Lot = self.env['stock.lot']
        for move_id, lines in by_move.items():
            move = self.env['stock.move'].browse(move_id)
            total = sum(lines.mapped('m2_total'))
            if abs(total - move.product_uom_qty) > 0.02:
                raise ValidationError(_(
                    '%(p)s: las planchas suman %(real).2f m2 y la recepcion '
                    'espera %(esperado).2f m2. Ajusta la cantidad o las medidas.',
                    p=move.product_id.display_name, real=total,
                    esperado=move.product_uom_qty))
            move.move_line_ids.unlink()
            move_lines = []
            for line in lines:
                codigos = Lot.siguiente_codigo(move.product_id, line.cantidad_planchas)
                for codigo in codigos:
                    lot = Lot.create({
                        'name': codigo,
                        'product_id': move.product_id.id,
                        'company_id': self.picking_id.company_id.id,
                        'largo': line.largo,
                        'alto': line.alto,
                        'espesor': line.espesor,
                        'm2_neto': line.m2_por_plancha,
                        'condicion': line.condicion,
                        'ubicacion_ref': line.ubicacion_ref,
                        'ref_importacion': line.ref_importacion,
                        'fecha_ingreso': fields.Date.context_today(self),
                    })
                    move_lines.append((0, 0, {
                        'product_id': move.product_id.id,
                        'lot_id': lot.id,
                        'quantity': line.m2_por_plancha,
                        'location_id': move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                    }))
            move.move_line_ids = move_lines
        self.picking_id.message_post(body=_('Planchas registradas desde la recepcion. Valida el albaran para ingresar el stock.'))
        return {'type': 'ir.actions.act_window_close'}


class RecepcionPlanchasLinea(models.TransientModel):
    _name = 'pierinelli.recepcion.planchas.linea'
    _description = 'Detalle de planchas recibidas'

    wizard_id = fields.Many2one('pierinelli.recepcion.planchas', required=True, ondelete='cascade')
    move_id = fields.Many2one('stock.move', required=True, readonly=True)
    product_id = fields.Many2one(related='move_id.product_id', readonly=True)
    cantidad_planchas = fields.Integer('Planchas', default=1, required=True)
    largo = fields.Float('Largo (m)', digits=(6, 2), required=True)
    alto = fields.Float('Alto (m)', digits=(6, 2), required=True)
    espesor = fields.Float('Espesor (cm)', digits=(4, 1), default=2.0)
    m2_por_plancha = fields.Float('m2 por plancha', compute='_compute_m2', store=True)
    m2_total = fields.Float('m2 total', compute='_compute_m2', store=True)
    m2_recibidos = fields.Float('m2 esperados', related='move_id.product_uom_qty', readonly=True)
    condicion = fields.Selection([('estandar', 'Estandar'), ('oferta', 'Oferta'), ('liquidacion', 'Liquidacion')], default='estandar', required=True)
    ubicacion_ref = fields.Char('Ubicacion referencial')
    ref_importacion = fields.Char('Ref. importacion')

    @api.depends('cantidad_planchas', 'largo', 'alto')
    def _compute_m2(self):
        for line in self:
            line.m2_por_plancha = round((line.largo or 0) * (line.alto or 0), 2)
            line.m2_total = round(line.m2_por_plancha * (line.cantidad_planchas or 0), 2)
