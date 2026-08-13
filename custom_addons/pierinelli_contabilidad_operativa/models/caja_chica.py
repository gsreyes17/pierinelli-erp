from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CajaChica(models.Model):
    _name = 'pierinelli.caja.chica'
    _description = 'Caja chica'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_apertura desc, id desc'

    name = fields.Char(required=True, default='Caja chica', tracking=True)
    responsable_id = fields.Many2one('res.users', required=True, default=lambda s: s.env.user)
    journal_id = fields.Many2one('account.journal', required=True, domain=[('type', '=', 'cash')], string='Diario de efectivo')
    journal_reposicion_id = fields.Many2one('account.journal', domain=[('type', '=', 'bank')], string='Diario bancario de reposicion')
    cuenta_faltante_id = fields.Many2one('account.account', string='Cuenta de faltante de caja')
    cuenta_sobrante_id = fields.Many2one('account.account', string='Cuenta de sobrante de caja')
    currency_id = fields.Many2one('res.currency', required=True, default=lambda s: s.env.company.currency_id)
    fondo_fijo = fields.Monetary(required=True, currency_field='currency_id')
    apertura_move_id = fields.Many2one('account.move', readonly=True, copy=False, string='Asiento de apertura')
    fecha_apertura = fields.Date(default=fields.Date.context_today, required=True)
    fecha_cierre = fields.Date(readonly=True)
    state = fields.Selection([('borrador', 'Borrador'), ('abierta', 'Abierta'), ('cerrada', 'Cerrada')], default='borrador', tracking=True)
    movimiento_ids = fields.One2many('pierinelli.caja.chica.movimiento', 'caja_id')
    gastos = fields.Monetary(compute='_compute_saldos', currency_field='currency_id')
    saldo_teorico = fields.Monetary(compute='_compute_saldos', currency_field='currency_id')
    total_repuesto = fields.Monetary(compute='_compute_saldos', currency_field='currency_id')
    total_ajuste_arqueo = fields.Monetary(compute='_compute_saldos', currency_field='currency_id')
    arqueo_real = fields.Monetary('Efectivo contado', currency_field='currency_id')
    arqueo_confirmado = fields.Boolean('Arqueo fisico confirmado')
    diferencia_arqueo = fields.Monetary(compute='_compute_saldos', currency_field='currency_id')
    reposicion_ids = fields.One2many('pierinelli.caja.chica.reposicion', 'caja_id')
    arqueo_ids = fields.One2many('pierinelli.caja.chica.arqueo', 'caja_id')

    @api.constrains('currency_id')
    def _check_soles(self):
        for caja in self:
            if caja.currency_id.name != 'PEN':
                raise UserError(_('La caja chica se maneja solamente en soles (PEN).'))

    @api.depends('fondo_fijo', 'movimiento_ids.importe', 'movimiento_ids.state', 'reposicion_ids.importe', 'reposicion_ids.state', 'arqueo_ids.diferencia', 'arqueo_real')
    def _compute_saldos(self):
        for caja in self:
            caja.gastos = sum(caja.movimiento_ids.filtered(lambda m: m.state == 'contabilizado').mapped('importe'))
            caja.total_repuesto = sum(caja.reposicion_ids.filtered(lambda r: r.state == 'contabilizado').mapped('importe'))
            caja.total_ajuste_arqueo = sum(caja.arqueo_ids.mapped('diferencia'))
            caja.saldo_teorico = caja.fondo_fijo - caja.gastos + caja.total_repuesto + caja.total_ajuste_arqueo
            caja.diferencia_arqueo = caja.arqueo_real - caja.saldo_teorico

    def action_abrir(self):
        for caja in self:
            if caja.fondo_fijo > 0:
                cuenta_caja = caja.journal_id.default_account_id
                cuenta_banco = caja.journal_reposicion_id.default_account_id
                if not cuenta_caja or not cuenta_banco:
                    raise UserError(_('Configura las cuentas de los diarios de efectivo y banco antes de abrir la caja.'))
                asiento = self.env['account.move'].create({
                    'move_type': 'entry', 'journal_id': caja.journal_reposicion_id.id,
                    'date': caja.fecha_apertura, 'ref': _('Apertura %s') % caja.name,
                    'tipo_operacion_contable': 'caja_chica',
                    'line_ids': [
                        (0, 0, {'account_id': cuenta_caja.id, 'name': _('Fondo fijo de caja chica'), 'debit': caja.fondo_fijo}),
                        (0, 0, {'account_id': cuenta_banco.id, 'name': _('Fondo fijo de caja chica'), 'credit': caja.fondo_fijo}),
                    ],
                })
                asiento.action_post()
                caja.apertura_move_id = asiento.id
            caja.state = 'abierta'

    def action_cerrar(self):
        for caja in self:
            if caja.movimiento_ids.filtered(lambda m: m.state == 'borrador'):
                raise UserError(_('Contabiliza o elimina los movimientos en borrador antes de cerrar la caja.'))
            if not caja.arqueo_confirmado:
                raise UserError(_('Registra el efectivo contado y confirma el arqueo fisico antes de cerrar la caja.'))
            caja.write({'state': 'cerrada', 'fecha_cierre': fields.Date.context_today(self)})

    def action_reponer(self):
        for caja in self:
            if caja.state != 'abierta':
                raise UserError(_('La caja chica debe estar abierta para reponerla.'))
            if not caja.journal_reposicion_id or not caja.journal_reposicion_id.default_account_id:
                raise UserError(_('Selecciona un diario bancario con cuenta configurada para la reposicion.'))
            importe = caja.gastos - caja.total_repuesto
            if importe <= 0:
                raise UserError(_('No hay gastos pendientes de reponer.'))
            caja_cuenta = caja.journal_id.default_account_id
            if not caja_cuenta:
                raise UserError(_('Configura la cuenta del diario de efectivo.'))
            asiento = self.env['account.move'].create({
                'move_type': 'entry', 'journal_id': caja.journal_reposicion_id.id,
                'date': fields.Date.context_today(self), 'ref': _('Reposicion %s') % caja.name,
                'tipo_operacion_contable': 'caja_chica',
                'line_ids': [(0, 0, {'account_id': caja_cuenta.id, 'name': _('Reposicion de caja chica'), 'debit': importe}),
                             (0, 0, {'account_id': caja.journal_reposicion_id.default_account_id.id, 'name': _('Reposicion de caja chica'), 'credit': importe})],
            })
            asiento.action_post()
            # La reposicion solo puede generarse desde este flujo: la vista no
            # permite crearla manualmente, por eso se registra con sudo luego
            # de haber validado caja, diario e importe como el usuario actual.
            self.env['pierinelli.caja.chica.reposicion'].sudo().create({
                'caja_id': caja.id, 'importe': importe, 'move_id': asiento.id,
                'state': 'contabilizado',
            })

    def action_ajustar_arqueo(self):
        for caja in self:
            if caja.state != 'abierta':
                raise UserError(_('La caja chica debe estar abierta para ajustar el arqueo.'))
            if not caja.arqueo_confirmado:
                raise UserError(_('Registra y confirma el arqueo fisico antes de ajustar la diferencia.'))
            diferencia = caja.diferencia_arqueo
            if not diferencia:
                raise UserError(_('No existe una diferencia de arqueo por ajustar.'))
            cuenta_caja = caja.journal_id.default_account_id
            if not cuenta_caja:
                raise UserError(_('Configura la cuenta del diario de efectivo antes de ajustar el arqueo.'))
            if diferencia < 0:
                cuenta_contrapartida = caja.cuenta_faltante_id
                lineas = [
                    (0, 0, {'account_id': cuenta_contrapartida.id if cuenta_contrapartida else False, 'name': _('Faltante de arqueo'), 'debit': -diferencia}),
                    (0, 0, {'account_id': cuenta_caja.id, 'name': _('Faltante de arqueo'), 'credit': -diferencia}),
                ]
                mensaje = _('Configura la cuenta de faltante de caja antes de ajustar el arqueo.')
            else:
                cuenta_contrapartida = caja.cuenta_sobrante_id
                lineas = [
                    (0, 0, {'account_id': cuenta_caja.id, 'name': _('Sobrante de arqueo'), 'debit': diferencia}),
                    (0, 0, {'account_id': cuenta_contrapartida.id if cuenta_contrapartida else False, 'name': _('Sobrante de arqueo'), 'credit': diferencia}),
                ]
                mensaje = _('Configura la cuenta de sobrante de caja antes de ajustar el arqueo.')
            if not cuenta_contrapartida:
                raise UserError(mensaje)
            asiento = self.env['account.move'].create({
                'move_type': 'entry', 'journal_id': caja.journal_id.id,
                'date': fields.Date.context_today(self), 'ref': _('Ajuste de arqueo %s') % caja.name,
                'tipo_operacion_contable': 'ajuste', 'line_ids': lineas,
            })
            asiento.action_post()
            # El ajuste se crea solo después de las validaciones y el asiento
            # publicado anteriores; no se habilita alta manual por RPC.
            self.env['pierinelli.caja.chica.arqueo'].sudo().create({
                'caja_id': caja.id, 'diferencia': diferencia, 'move_id': asiento.id,
            })


class CajaChicaReposicion(models.Model):
    _name = 'pierinelli.caja.chica.reposicion'
    _description = 'Reposicion bancaria de caja chica'
    _order = 'id desc'

    caja_id = fields.Many2one('pierinelli.caja.chica', required=True, ondelete='cascade')
    fecha = fields.Date(default=fields.Date.context_today, required=True)
    importe = fields.Monetary(required=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='caja_id.currency_id')
    move_id = fields.Many2one('account.move', readonly=True)
    state = fields.Selection([('contabilizado', 'Contabilizado')], default='contabilizado')


class CajaChicaArqueo(models.Model):
    _name = 'pierinelli.caja.chica.arqueo'
    _description = 'Ajuste de arqueo de caja chica'
    _order = 'id desc'

    caja_id = fields.Many2one('pierinelli.caja.chica', required=True, ondelete='cascade')
    fecha = fields.Date(default=fields.Date.context_today, required=True)
    diferencia = fields.Monetary(required=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='caja_id.currency_id')
    move_id = fields.Many2one('account.move', readonly=True)


class CajaChicaMovimiento(models.Model):
    _name = 'pierinelli.caja.chica.movimiento'
    _description = 'Movimiento de caja chica'
    _order = 'fecha desc, id desc'

    caja_id = fields.Many2one('pierinelli.caja.chica', required=True, ondelete='cascade')
    company_id = fields.Many2one(related='caja_id.journal_id.company_id')
    fecha = fields.Date(default=fields.Date.context_today, required=True)
    partner_id = fields.Many2one('res.partner', string='Proveedor / beneficiario')
    tipo_comprobante_id = fields.Many2one(
        'pierinelli.tipo.comprobante', string='Tipo de sustento',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    cuenta_gasto_id = fields.Many2one('account.account', required=True, string='Cuenta de gasto')
    importe = fields.Monetary(required=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='caja_id.currency_id')
    documento = fields.Char('Factura, boleta o planilla de movilidad')
    descripcion = fields.Char(required=True)
    move_id = fields.Many2one('account.move', readonly=True, copy=False)
    state = fields.Selection([('borrador', 'Borrador'), ('contabilizado', 'Contabilizado')], default='borrador')

    def action_contabilizar(self):
        for mov in self:
            if mov.caja_id.state != 'abierta':
                raise UserError(_('La caja chica debe estar abierta.'))
            cuenta_caja = mov.caja_id.journal_id.default_account_id
            if not cuenta_caja:
                raise UserError(_('Configura la cuenta del diario de efectivo antes de contabilizar.'))
            asiento = self.env['account.move'].create({
                'move_type': 'entry', 'journal_id': mov.caja_id.journal_id.id,
                'date': mov.fecha, 'ref': mov.documento or mov.caja_id.name,
                'tipo_operacion_contable': 'caja_chica',
                'line_ids': [(0, 0, {'account_id': mov.cuenta_gasto_id.id, 'name': mov.descripcion, 'debit': mov.importe}),
                             (0, 0, {'account_id': cuenta_caja.id, 'name': mov.descripcion, 'credit': mov.importe})],
            })
            asiento.action_post()
            mov.write({'move_id': asiento.id, 'state': 'contabilizado'})
