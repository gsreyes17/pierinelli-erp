# -*- coding: utf-8 -*-
"""
Alta masiva de planchas (Plan V2, Fase 2 tarea 9).

El almacenero escribe "20 planchas de 3.40 x 1.65" y el sistema genera los
lotes CIG1025.01 ... CIG1025.20 con sus medidas y su stock, de un golpe.
Las que midan distinto se corrigen despues en su ficha.
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AltaPlanchas(models.TransientModel):
    _name = 'pierinelli.alta.planchas'
    _description = 'Alta masiva de planchas'

    product_id = fields.Many2one(
        'product.product', string='Producto', required=True,
        domain=[('is_storable', '=', True), ('tracking', '=', 'lot')])
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Almacen', required=True,
        default=lambda self: self.env['stock.warehouse'].search([], limit=1))
    cantidad = fields.Integer(
        string='Numero de planchas', default=1, required=True)
    largo = fields.Float('Largo (m)', digits=(6, 2), required=True)
    alto = fields.Float('Alto (m)', digits=(6, 2), required=True)
    espesor = fields.Float('Espesor (cm)', digits=(4, 1), default=2.0)
    condicion = fields.Selection(
        [('estandar', 'Estandar'),
         ('oferta', 'Oferta'),
         ('liquidacion', 'Liquidacion')],
        string='Condicion', default='estandar', required=True)
    ubicacion_ref = fields.Char('Ubicacion referencial')
    ref_importacion = fields.Char('Ref. importacion')
    m2_por_plancha = fields.Float(
        'm² por plancha', compute='_compute_m2', digits=(8, 2))
    m2_total = fields.Float('m² total', compute='_compute_m2', digits=(8, 2))
    codigos_preview = fields.Char(
        'Codigos a generar', compute='_compute_preview')

    @api.depends('largo', 'alto', 'cantidad')
    def _compute_m2(self):
        for wiz in self:
            wiz.m2_por_plancha = round((wiz.largo or 0) * (wiz.alto or 0), 2)
            wiz.m2_total = round(wiz.m2_por_plancha * (wiz.cantidad or 0), 2)

    @api.depends('product_id', 'cantidad')
    def _compute_preview(self):
        Lot = self.env['stock.lot']
        for wiz in self:
            if not wiz.product_id or wiz.cantidad <= 0:
                wiz.codigos_preview = False
                continue
            codigos = Lot.siguiente_codigo(wiz.product_id, count=wiz.cantidad)
            if len(codigos) > 1:
                wiz.codigos_preview = '%s … %s' % (codigos[0], codigos[-1])
            else:
                wiz.codigos_preview = codigos[0]

    def action_crear(self):
        self.ensure_one()
        if self.cantidad <= 0:
            raise UserError(_('El numero de planchas debe ser mayor a cero.'))
        if self.largo <= 0 or self.alto <= 0:
            raise UserError(_('Largo y alto deben ser mayores a cero.'))

        Lot = self.env['stock.lot']
        Quant = self.env['stock.quant']
        hoy = fields.Date.context_today(self)
        m2 = round(self.largo * self.alto, 2)
        codigos = Lot.siguiente_codigo(
            self.product_id, count=self.cantidad, fecha=hoy)

        planchas = Lot.browse()
        for codigo in codigos:
            lot = Lot.create({
                'name': codigo,
                'product_id': self.product_id.id,
                'company_id': self.env.company.id,
                'largo': self.largo,
                'alto': self.alto,
                'espesor': self.espesor,
                'm2_neto': m2,
                'condicion': self.condicion,
                'ubicacion_ref': self.ubicacion_ref,
                'ref_importacion': self.ref_importacion,
                'fecha_ingreso': hoy,
            })
            # La foto individual es para naturales; en artificiales todas
            # comparten la imagen del producto, que ya esta en el catalogo.
            Quant._update_available_quantity(
                self.product_id, self.warehouse_id.lot_stock_id, m2,
                lot_id=lot)
            planchas |= lot

        action = self.env['ir.actions.act_window']._for_xml_id(
            'pierinelli_planchas.action_planchas_operaciones')
        action['domain'] = [('id', 'in', planchas.ids)]
        return action
