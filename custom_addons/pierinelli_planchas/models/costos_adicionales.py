from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


CONCEPTOS_COSTO = [
    ('flete', 'Flete / viaje'),
    ('seguridad', 'Seguridad de traslado'),
    ('seguro', 'Seguro de carga'),
    ('aduana', 'Aduana / importación'),
    ('maniobra', 'Carga, descarga o maniobra'),
    ('otro', 'Otro costo'),
]


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    costo_adicional_ids = fields.One2many(
        'pierinelli.costo.adicional', 'picking_id', string='Costos adicionales')
    currency_id = fields.Many2one(
        related='company_id.currency_id', string='Moneda')
    costo_adicional_total = fields.Monetary(
        compute='_compute_costo_adicional_total', string='Total costos adicionales',
        currency_field='currency_id')
    landed_cost_id = fields.Many2one(
        'stock.landed.cost', string='Costeo generado', readonly=True, copy=False)

    @api.depends('costo_adicional_ids.importe')
    def _compute_costo_adicional_total(self):
        for picking in self:
            picking.costo_adicional_total = sum(picking.costo_adicional_ids.mapped('importe'))

    def _check_costeo_aplicable(self):
        self.ensure_one()
        if self.picking_type_code not in ('incoming', 'internal'):
            raise UserError(_('Los costos adicionales solo aplican a recepciones o transferencias internas.'))
        if self.state != 'done':
            raise UserError(_('Primero valide la recepción o transferencia antes de preparar su costeo.'))
        if not self.costo_adicional_ids:
            raise UserError(_('Registra al menos un costo adicional.'))
        moves = self.move_ids.filtered(
            lambda move: move.state != 'cancel' and move.quantity and
            move.product_id.cost_method in ('average', 'fifo'))
        if not moves:
            raise UserError(_(
                'No hay productos valorizables en esta operación. Para costear, '
                'los productos deben usar costo Promedio o FIFO.'))

    def _get_producto_costo(self, concepto):
        """Devuelve un servicio de costo en destino; se crea una vez por concepto."""
        self.ensure_one()
        code = 'PIER-COST-%s' % concepto.upper()
        product = self.env['product.product'].search([('default_code', '=', code)], limit=1)
        if product:
            return product

        template = self.env['product.template'].search(
            [('landed_cost_ok', '=', True)], limit=1)
        category = template.categ_id if template else self.env.ref('product.product_category_all')
        name = dict(CONCEPTOS_COSTO).get(concepto, _('Costo adicional'))
        # Es una configuracion tecnica creada una sola vez por concepto. El
        # usuario de almacen no necesita permisos de Productos para usarla.
        template = self.env['product.template'].sudo().create({
            'name': _('Costo en destino - %s') % name,
            'default_code': code,
            'type': 'service',
            'categ_id': category.id,
            'landed_cost_ok': True,
            'split_method_landed_cost': 'by_quantity',
        })
        return template.product_variant_id

    def action_preparar_costeo(self):
        self._check_costeo_aplicable()
        if self.landed_cost_id:
            return self.action_ver_costeo()

        lineas = []
        for costo in self.costo_adicional_ids:
            product = self._get_producto_costo(costo.concepto)
            accounts = product.product_tmpl_id.get_product_accounts()
            lineas.append((0, 0, {
                'product_id': product.id,
                'name': costo.detalle or dict(CONCEPTOS_COSTO)[costo.concepto],
                'price_unit': costo.importe,
                'split_method': costo.metodo_reparto,
                'account_id': accounts['expense'].id if accounts.get('expense') else False,
            }))

        landed_cost = self.env['stock.landed.cost'].create({
            'date': self.date_done.date() if self.date_done else fields.Date.context_today(self),
            'picking_ids': [(6, 0, self.ids)],
            'cost_lines': lineas,
            'description': _('Costos adicionales de %s') % self.name,
        })
        self.landed_cost_id = landed_cost.id
        return self.action_ver_costeo()

    def action_ver_costeo(self):
        self.ensure_one()
        if not self.landed_cost_id:
            raise UserError(_('Aún no se preparó un costeo para esta operación.'))
        action = self.env['ir.actions.actions']._for_xml_id(
            'stock_landed_costs.action_stock_landed_cost')
        return dict(action, view_mode='form', res_id=self.landed_cost_id.id,
                    views=[(False, 'form')])


class CostoAdicionalPicking(models.Model):
    _name = 'pierinelli.costo.adicional'
    _description = 'Costo adicional de recepción o transferencia'
    _order = 'id'

    picking_id = fields.Many2one('stock.picking', required=True, ondelete='cascade')
    concepto = fields.Selection(CONCEPTOS_COSTO, required=True, default='flete')
    detalle = fields.Char('Detalle', required=True, default='Flete')
    importe = fields.Monetary(required=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='picking_id.currency_id')
    metodo_reparto = fields.Selection([
        ('by_quantity', 'Por cantidad / m²'),
        ('equal', 'En partes iguales'),
        ('by_current_cost_price', 'Según valor actual'),
        ('by_weight', 'Según peso'),
        ('by_volume', 'Según volumen'),
    ], required=True, default='by_quantity', string='Repartir costo')

    @api.constrains('importe')
    def _check_importe(self):
        for costo in self:
            if costo.importe <= 0:
                raise ValidationError(_('El importe del costo adicional debe ser mayor que cero.'))

    @api.constrains('picking_id')
    def _check_picking(self):
        for costo in self:
            if costo.picking_id.picking_type_code not in ('incoming', 'internal'):
                raise ValidationError(_(
                    'Solo se pueden cargar costos adicionales en recepciones o transferencias internas.'))
