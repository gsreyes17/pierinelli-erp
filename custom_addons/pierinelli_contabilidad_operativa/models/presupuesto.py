from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PresupuestoFinanciero(models.Model):
    _name = 'pierinelli.presupuesto.financiero'
    _description = 'Presupuesto financiero'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_inicio desc, id desc'

    name = fields.Char(required=True, default='Presupuesto')
    fecha_inicio = fields.Date(required=True, default=lambda s: fields.Date.context_today(s).replace(day=1))
    fecha_fin = fields.Date(required=True)
    company_id = fields.Many2one('res.company', default=lambda s: s.env.company, required=True)
    currency_id = fields.Many2one(related='company_id.currency_id')
    state = fields.Selection([('borrador', 'Borrador'), ('aprobado', 'Aprobado'), ('cerrado', 'Cerrado')], default='borrador', tracking=True)
    linea_ids = fields.One2many('pierinelli.presupuesto.financiero.linea', 'presupuesto_id')
    total_presupuestado = fields.Monetary(compute='_compute_totales', currency_field='currency_id')
    total_ejecutado = fields.Monetary(compute='_compute_totales', currency_field='currency_id')

    @api.depends('linea_ids.presupuestado', 'linea_ids.ejecutado')
    def _compute_totales(self):
        for rec in self:
            rec.total_presupuestado = sum(rec.linea_ids.mapped('presupuestado'))
            rec.total_ejecutado = sum(rec.linea_ids.mapped('ejecutado'))

    def action_aprobar(self):
        for rec in self:
            if not rec.linea_ids:
                raise UserError(_('Agrega al menos una linea presupuestal.'))
            rec.state = 'aprobado'

    def action_cerrar(self): self.write({'state': 'cerrado'})


class PresupuestoFinancieroLinea(models.Model):
    _name = 'pierinelli.presupuesto.financiero.linea'
    _description = 'Linea de presupuesto financiero'

    presupuesto_id = fields.Many2one('pierinelli.presupuesto.financiero', required=True, ondelete='cascade')
    cuenta_id = fields.Many2one('account.account', required=True, string='Cuenta contable')
    centro_costo_id = fields.Many2one('account.analytic.account', string='Centro de costo / obra')
    presupuestado = fields.Monetary(required=True, currency_field='currency_id')
    ejecutado = fields.Monetary(compute='_compute_ejecutado', currency_field='currency_id')
    saldo = fields.Monetary(compute='_compute_ejecutado', currency_field='currency_id')
    porcentaje = fields.Float(compute='_compute_ejecutado')
    currency_id = fields.Many2one(related='presupuesto_id.currency_id')

    @api.depends('cuenta_id', 'centro_costo_id', 'presupuesto_id.fecha_inicio', 'presupuesto_id.fecha_fin', 'presupuestado')
    def _compute_ejecutado(self):
        MoveLine = self.env['account.move.line']
        for line in self:
            if not line.cuenta_id or not line.presupuesto_id.fecha_inicio or not line.presupuesto_id.fecha_fin:
                line.ejecutado = line.saldo = line.porcentaje = 0
                continue
            domain = [('parent_state', '=', 'posted'), ('account_id', '=', line.cuenta_id.id),
                      ('date', '>=', line.presupuesto_id.fecha_inicio), ('date', '<=', line.presupuesto_id.fecha_fin)]
            move_lines = MoveLine.search(domain)
            if line.centro_costo_id:
                analytic_id = str(line.centro_costo_id.id)
                # analytic_distribution guarda porcentajes por cuenta analítica
                # en JSON, y la clave puede ser COMPUESTA cuando la linea se
                # distribuye entre cuentas de varios planes a la vez: {'12,15':
                # 100.0} (asi las serializa analytic_mixin, que itera
                # key.split(',')). Un .get(str(id)) exacto ignoraria esos
                # importes y subreportaria el ejecutado.
                amount = 0.0
                for move_line in move_lines:
                    for key, pct in (move_line.analytic_distribution or {}).items():
                        if analytic_id in str(key).split(','):
                            amount += move_line.balance * float(pct) / 100.0
            else:
                amount = sum(move_lines.mapped('balance'))
            line.ejecutado = abs(amount)
            line.saldo = line.presupuestado - line.ejecutado
            line.porcentaje = (line.ejecutado / line.presupuestado * 100) if line.presupuestado else 0
