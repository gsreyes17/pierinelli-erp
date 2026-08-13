from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    numero_externo = fields.Char(
        'Numero externo SUNAT', copy=False,
        help='Solo para comprobantes emitidos externamente. No reemplaza la '
             'secuencia interna del asiento.')
    tipo_operacion_contable = fields.Selection([
        ('venta', 'Venta'), ('compra', 'Compra'), ('anticipo', 'Anticipo'),
        ('detraccion', 'Detraccion'), ('retencion', 'Retencion'),
        ('nota_credito', 'Nota de credito'), ('caja_chica', 'Caja chica'),
        ('provision', 'Provision'), ('depreciacion', 'Depreciacion'),
        ('ajuste', 'Ajuste manual'),
    ], string='Tipo de operacion', copy=False)
    tipo_comprobante_id = fields.Many2one(
        'pierinelli.tipo.comprobante', string='Tipo de comprobante',
        copy=False, check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help='Clasifica el sustento del comprobante. No reemplaza la serie ni '
             'el correlativo de Odoo o SUNAT.')
    clasificacion_compra = fields.Selection([
        ('mercaderia', 'Mercaderías'),
        ('servicio', 'Servicios'),
        ('gasto', 'Gastos'),
        ('activo_fijo', 'Activo fijo'),
        ('otro', 'Otro'),
    ], string='Clasificación de compra', copy=False,
       help='Control interno para separar compras de mercadería, servicios, '
            'gastos y activos. La cuenta contable sigue siendo la que define '
            'el asiento.')
    tributo_ids = fields.One2many('pierinelli.control.tributario', 'move_id', string='Controles SUNAT')


class ControlTributario(models.Model):
    _name = 'pierinelli.control.tributario'
    _description = 'Control de detraccion o retencion'
    _order = 'fecha desc, id desc'

    move_id = fields.Many2one('account.move', required=True, ondelete='cascade', string='Comprobante')
    tipo = fields.Selection([('detraccion', 'Detraccion'), ('retencion', 'Retencion IGV')], required=True)
    porcentaje = fields.Float(required=True, digits=(5, 2))
    base = fields.Monetary(required=True, currency_field='currency_id')
    importe = fields.Monetary(compute='_compute_importe', store=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='move_id.currency_id', store=True)
    fecha = fields.Date(default=fields.Date.context_today, required=True)
    constancia = fields.Char('Constancia / referencia de pago')
    estado = fields.Selection([('pendiente', 'Pendiente'), ('pagado', 'Pagado')], default='pendiente', required=True)
    notas = fields.Char()

    @api.depends('base', 'porcentaje')
    def _compute_importe(self):
        for rec in self:
            rec.importe = round(rec.base * rec.porcentaje / 100, 2)
