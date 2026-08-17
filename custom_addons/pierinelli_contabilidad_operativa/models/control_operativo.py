from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class TipoComprobante(models.Model):
    _name = 'pierinelli.tipo.comprobante'
    _description = 'Tipo de comprobante y sustento'
    _order = 'scope, code, name'
    _check_company_auto = True

    name = fields.Char(required=True)
    code = fields.Char('Código', required=True)
    scope = fields.Selection([
        ('venta', 'Ventas'), ('compra', 'Compras'), ('caja', 'Caja chica'),
        ('interno', 'Control interno'),
    ], required=True, default='compra')
    company_id = fields.Many2one('res.company', string='Compañía')
    active = fields.Boolean(default=True)
    requiere_ruc = fields.Boolean('Requiere RUC')
    permite_credito_fiscal = fields.Boolean('Permite crédito fiscal')
    notas = fields.Char('Notas / regla interna')

    _code_company_unique = models.Constraint(
        'unique(code, company_id)',
        'Ya existe un tipo de comprobante con ese código para esta compañía.',
    )

    def name_get(self):
        return [(rec.id, '%s · %s' % (rec.code, rec.name)) for rec in self]


class ArqueoCobranza(models.Model):
    _name = 'pierinelli.arqueo.cobranza'
    _description = 'Arqueo diario de cobranzas'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha desc, id desc'
    _check_company_auto = True

    name = fields.Char(required=True, default=lambda self: _(
        'Arqueo de cobranzas'))
    fecha = fields.Date(required=True, default=fields.Date.context_today,
                        tracking=True)
    journal_id = fields.Many2one(
        'account.journal', required=True, string='Diario de efectivo',
        domain=[('type', '=', 'cash')], check_company=True)
    company_id = fields.Many2one(related='journal_id.company_id', store=True)
    currency_id = fields.Many2one(
        'res.currency', compute='_compute_currency', store=True,
        string='Moneda')
    payment_ids = fields.Many2many(
        'account.payment', compute='_compute_cobros',
        string='Cobros incluidos')
    importe_esperado = fields.Monetary(
        compute='_compute_cobros', currency_field='currency_id',
        string='Efectivo esperado')
    efectivo_contado = fields.Monetary(
        string='Efectivo contado', currency_field='currency_id', tracking=True)
    diferencia = fields.Monetary(
        compute='_compute_diferencia', currency_field='currency_id')
    arqueo_confirmado = fields.Boolean('Conteo físico confirmado', tracking=True)
    observacion = fields.Text('Observación / depósito')
    state = fields.Selection([
        ('borrador', 'Borrador'), ('cerrado', 'Cerrado'),
    ], default='borrador', tracking=True)

    _fecha_diario_moneda_unique = models.Constraint(
        'unique(fecha, journal_id, currency_id)',
        'Ya existe un arqueo para esa fecha, diario y moneda.',
    )

    @api.depends('journal_id', 'journal_id.currency_id',
                 'journal_id.company_id.currency_id')
    def _compute_currency(self):
        for rec in self:
            rec.currency_id = (rec.journal_id.currency_id
                               or rec.journal_id.company_id.currency_id)

    @api.depends('fecha', 'journal_id', 'currency_id')
    def _compute_cobros(self):
        Payment = self.env['account.payment']
        for rec in self:
            if not rec.fecha or not rec.journal_id or not rec.currency_id:
                rec.payment_ids = False
                rec.importe_esperado = 0.0
                continue
            payments = Payment.search([
                ('date', '=', rec.fecha),
                ('journal_id', '=', rec.journal_id.id),
                ('payment_type', '=', 'inbound'),
                ('state', '=', 'paid'),
                ('currency_id', '=', rec.currency_id.id),
            ])
            rec.payment_ids = payments
            rec.importe_esperado = sum(payments.mapped('amount'))

    @api.depends('importe_esperado', 'efectivo_contado')
    def _compute_diferencia(self):
        for rec in self:
            rec.diferencia = rec.efectivo_contado - rec.importe_esperado

    def action_cerrar(self):
        for rec in self:
            if not rec.arqueo_confirmado:
                raise UserError(_(
                    'Ingresa el efectivo contado y confirma el conteo físico '
                    'antes de cerrar el arqueo.'))
            rec.state = 'cerrado'

    def action_reabrir(self):
        if not (self.env.user.has_group('account.group_account_manager')
                or self.env.user.has_group('base.group_system')):
            raise AccessError(_(
                'Solo un responsable contable puede reabrir un arqueo cerrado.'))
        self.write({'state': 'borrador'})


class CierreContable(models.Model):
    _name = 'pierinelli.cierre.contable'
    _description = 'Control de cierre contable'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_bloqueo desc, id desc'
    _check_company_auto = True

    name = fields.Char(required=True, default='Cierre contable')
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company)
    fecha_bloqueo = fields.Date('Bloquear hasta', required=True)
    tipo = fields.Selection([
        ('fiscal', 'Cierre contable'),
        ('impuesto', 'Cierre tributario'),
        ('ventas', 'Cierre de ventas'),
    ], default='fiscal', required=True)
    fecha_anterior = fields.Date('Bloqueo anterior', readonly=True)
    fecha_aplicacion = fields.Date('Fecha de aplicación', readonly=True)
    aplicado_por_id = fields.Many2one('res.users', readonly=True)
    state = fields.Selection([
        ('borrador', 'Borrador'), ('aplicado', 'Aplicado'),
        ('revertido', 'Revertido'),
    ], default='borrador', tracking=True)
    observacion = fields.Text('Sustento del cierre')

    def _check_manager(self):
        if not (self.env.user.has_group('account.group_account_manager')
                or self.env.user.has_group('base.group_system')):
            raise AccessError(_(
                'Solo un responsable contable o Administrador puede aplicar '
                'un cierre.'))

    def _company_lock_field(self):
        return {
            'fiscal': 'fiscalyear_lock_date',
            'impuesto': 'tax_lock_date',
            'ventas': 'sale_lock_date',
        }[self.tipo]

    def action_aplicar(self):
        self._check_manager()
        for rec in self:
            if rec.state != 'borrador':
                raise UserError(_('Solo se puede aplicar un cierre en borrador.'))
            lock_field = rec._company_lock_field()
            previous = rec.company_id[lock_field]
            if previous and rec.fecha_bloqueo < previous:
                raise ValidationError(_(
                    'La fecha no puede ser anterior al bloqueo vigente (%s).')
                    % previous)
            # sudo() imprescindible: el ACL de base solo permite escribir
            # res.company a group_erp_manager, y esta funcion es para el
            # responsable contable (ya validado en _check_manager). Sin esto,
            # el contador pasa el check propio y recibe AccessError del ORM.
            rec.company_id.sudo().write({lock_field: rec.fecha_bloqueo})
            rec.write({
                'fecha_anterior': previous,
                'fecha_aplicacion': fields.Date.context_today(rec),
                'aplicado_por_id': self.env.user.id,
                'state': 'aplicado',
            })

    def action_revertir(self):
        self._check_manager()
        for rec in self:
            if rec.state != 'aplicado':
                raise UserError(_('Solo se puede revertir un cierre aplicado.'))
            lock_field = rec._company_lock_field()
            if rec.company_id[lock_field] != rec.fecha_bloqueo:
                raise UserError(_(
                    'No se puede revertir porque existe un bloqueo posterior.'))
            rec.company_id.sudo().write({lock_field: rec.fecha_anterior})
            rec.state = 'revertido'
