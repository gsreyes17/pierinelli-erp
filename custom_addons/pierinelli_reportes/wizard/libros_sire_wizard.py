# -*- coding: utf-8 -*-
import base64
import io
from collections import defaultdict
from datetime import date, timedelta
from urllib.parse import quote

from odoo import Command, _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

try:
    import xlsxwriter
except ImportError:  # pragma: no cover - Odoo lo incluye en su imagen oficial
    xlsxwriter = None


REPORT_TYPES = [
    ('ventas_141', 'Registro de Ventas 14.1 / vista RVIE'),
    ('compras_81', 'Registro de Compras 8.1 / vista RCE'),
    ('compras_82', 'Registro de Compras 8.2 - no domiciliados'),
    ('caja_11', 'Libro Caja y Bancos 1.1 - efectivo'),
    ('bancos_12', 'Libro Caja y Bancos 1.2 - cuentas bancarias'),
    ('inventarios_balances', 'Libro de Inventarios y Balances - resumen 3.x'),
    ('activos_71', 'Registro de Activos Fijos 7.1 - base de revisión'),
    ('kardex_131', 'Inventario Permanente Valorizado 13.1 / Kardex'),
    ('guias', 'Guías de remisión y entregas'),
    ('almacenes', 'Existencias por almacén, ubicación y lote'),
    ('diario_clasico', 'Libro Diario clásico - asientos, Debe y Haber'),
    ('mayor_clasico', 'Libro Mayor clásico - movimientos por cuenta'),
    ('balance_comprobacion', 'Balance de Comprobación - sumas y saldos'),
]

ACCOUNTING_REPORT_TYPES = ('diario_clasico', 'mayor_clasico', 'balance_comprobacion')

STATUS_LABELS = {
    'draft': 'Borrador', 'posted': 'Publicado', 'cancel': 'Anulado',
    'not_paid': 'No pagado', 'in_payment': 'En pago', 'paid': 'Pagado',
    'partial': 'Pago parcial', 'reversed': 'Revertido',
    'waiting': 'En espera', 'confirmed': 'En espera', 'assigned': 'Listo',
    'done': 'Hecho',
}


class LibrosSireWizard(models.TransientModel):
    _name = 'pierinelli.libros.sire.wizard'
    _description = 'Centro de Libros y preparación SIRE'

    @api.model
    def _default_date_from(self):
        today = fields.Date.context_today(self)
        return today.replace(day=1)

    report_type = fields.Selection(
        REPORT_TYPES, string='Libro o reporte', required=True, default='ventas_141')
    date_from = fields.Date(
        string='Desde', required=True, default=_default_date_from)
    date_to = fields.Date(
        string='Hasta', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one(
        'res.company', string='Empresa', required=True,
        default=lambda self: self.env.company)
    target_move = fields.Selection([
        ('posted', 'Solo publicados / realizados'),
        ('all', 'Incluir borradores'),
    ], string='Estado', required=True, default='posted')
    account_id = fields.Many2one(
        'account.account', string='Cuenta contable', check_company=True,
        domain="[('company_ids', 'in', company_id)]",
        help='Filtro opcional para el Libro Mayor clásico.')
    line_ids = fields.One2many(
        'pierinelli.libros.sire.line', 'wizard_id', string='Vista previa', readonly=True)
    line_count = fields.Integer(string='Filas', compute='_compute_line_count')
    export_file = fields.Binary(string='Archivo generado', readonly=True, attachment=False)
    export_filename = fields.Char(string='Nombre del archivo', readonly=True)
    prepared = fields.Boolean(string='Vista preparada', readonly=True)
    preview_note = fields.Char(string='Mensaje de vista previa', readonly=True)
    mayor_summary = fields.Char(string='Resumen de cuenta', readonly=True)
    mayor_opening_debit = fields.Float(string='Saldo anterior deudor', readonly=True)
    mayor_opening_credit = fields.Float(string='Saldo anterior acreedor', readonly=True)
    mayor_movement_debit = fields.Float(string='Movimientos Debe', readonly=True)
    mayor_movement_credit = fields.Float(string='Movimientos Haber', readonly=True)
    mayor_closing_debit = fields.Float(string='Saldo deudor', readonly=True)
    mayor_closing_credit = fields.Float(string='Saldo acreedor', readonly=True)

    @api.depends('line_ids')
    def _compute_line_count(self):
        for wizard in self:
            wizard.line_count = len(wizard.line_ids)

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for wizard in self:
            if wizard.date_from and wizard.date_to and wizard.date_from > wizard.date_to:
                raise ValidationError(_('La fecha inicial no puede ser posterior a la final.'))

    def _check_company_access(self):
        self.ensure_one()
        if self.company_id not in self.env.companies:
            raise AccessError(_('No tiene acceso a la empresa seleccionada.'))

    @api.onchange('report_type', 'date_from', 'date_to', 'company_id', 'target_move', 'account_id')
    def _onchange_filters(self):
        self.prepared = False
        self.line_ids = [Command.clear()]
        self.export_file = False
        self.export_filename = False
        self.preview_note = False
        self.mayor_summary = False
        self.mayor_opening_debit = 0
        self.mayor_opening_credit = 0
        self.mayor_movement_debit = 0
        self.mayor_movement_credit = 0
        self.mayor_closing_debit = 0
        self.mayor_closing_credit = 0

    def _report_label(self):
        self.ensure_one()
        return dict(REPORT_TYPES).get(self.report_type, self.report_type)

    @staticmethod
    def _document_parts(name):
        text = (name or '').strip()
        if '-' in text:
            series, number = text.split('-', 1)
            return series, number
        return '', text

    @staticmethod
    def _partner_id_type(partner):
        id_type = getattr(partner, 'l10n_latam_identification_type_id', False)
        return getattr(id_type, 'l10n_pe_vat_code', '') or ''

    @staticmethod
    def _document_type(move):
        doc_type = getattr(move, 'l10n_latam_document_type_id', False)
        return getattr(doc_type, 'code', '') or (move.journal_id.code or '')

    @staticmethod
    def _product_summary(lines):
        product_lines = lines.filtered(lambda line: line.display_type == 'product')
        names = []
        for line in product_lines[:3]:
            name = line.product_id.display_name or line.name or ''
            if name and name not in names:
                names.append(name)
        if len(product_lines) > 3:
            names.append(_('y %s línea(s) más') % (len(product_lines) - 3))
        return ', '.join(names), sum(product_lines.mapped('quantity'))

    def _invoice_rows(self, move_types, non_resident=False):
        self.ensure_one()
        domain = [
            ('company_id', '=', self.company_id.id),
            ('move_type', 'in', move_types),
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
        ]
        domain.append(('state', '=', 'posted') if self.target_move == 'posted'
                      else ('state', 'in', ('draft', 'posted')))
        moves = self.env['account.move'].sudo().search(domain, order='invoice_date, name, id')
        rows = []
        company_country = self.company_id.country_id
        for move in moves:
            is_foreign = bool(
                move.partner_id.country_id and company_country
                and move.partner_id.country_id != company_country)
            if non_resident and not is_foreign:
                continue
            if not non_resident and self.report_type == 'compras_81' and is_foreign:
                continue
            sign = -1 if move.move_type in ('out_refund', 'in_refund') else 1
            official_number = getattr(move, 'l10n_latam_document_number', False)
            series, number = self._document_parts(official_number or move.name or move.ref)
            product_summary, quantity = self._product_summary(move.invoice_line_ids)
            payment = STATUS_LABELS.get(move.payment_state, move.payment_state or '')
            rows.append({
                'date': move.invoice_date,
                'operation': self._document_type(move),
                'series': series,
                'document': number,
                'partner': move.partner_id.display_name,
                'vat': move.partner_id.vat or '',
                'id_type': self._partner_id_type(move.partner_id),
                'description': product_summary,
                'quantity': sign * quantity,
                'currency': move.currency_id.name,
                'base': sign * move.amount_untaxed,
                'tax': sign * move.amount_tax,
                'total': sign * move.amount_total,
                'status': '%s · %s' % (STATUS_LABELS.get(move.state, move.state), payment),
                'extra': move.ref or move.invoice_origin or '',
                'correlative': '%s%04d' % (move.invoice_date.strftime('%Y%m'), len(rows) + 1),
                'cuo': '%s00-%s' % (move.invoice_date.strftime('%Y%m'), len(rows) + 1),
                'other_tax': 0.0,
                'detraction': self._get_detraction_certificate(move),
            })
        return rows

    def _get_detraction_certificate(self, move):
        """Obtiene la constancia si el complemento operativo está instalado."""
        model = self.env.registry.get('pierinelli.control.tributario')
        if not model:
            return ''
        record = self.env['pierinelli.control.tributario'].sudo().search([
            ('move_id', '=', move.id), ('tipo', '=', 'detraccion'),
        ], limit=1)
        return record.constancia or ''

    def _cash_bank_rows(self, journal_type):
        self.ensure_one()
        domain = [
            ('company_id', '=', self.company_id.id),
            ('date', '>=', self.date_from), ('date', '<=', self.date_to),
            ('journal_id.type', '=', journal_type),
            ('account_id.account_type', '=', 'asset_cash'),
        ]
        domain.append(('parent_state', '=', 'posted') if self.target_move == 'posted'
                      else ('parent_state', 'in', ('draft', 'posted')))
        lines = self.env['account.move.line'].sudo().search(domain, order='date, move_name, id')
        return [{
            'date': line.date,
            'operation': line.journal_id.code,
            'series': '',
            'document': line.move_name,
            'partner': line.partner_id.display_name or '',
            'vat': line.partner_id.vat or '',
            'id_type': self._partner_id_type(line.partner_id),
            'description': line.name or line.account_id.display_name,
            'quantity': 0,
            'currency': line.company_currency_id.name,
            'base': line.debit,
            'tax': line.credit,
            'total': line.balance,
            'status': STATUS_LABELS.get(line.parent_state, line.parent_state),
            'extra': line.account_id.code,
        } for line in lines]

    def _inventory_balance_rows(self):
        self.ensure_one()
        state_domain = [('parent_state', '=', 'posted')] if self.target_move == 'posted' else []
        lines = self.env['account.move.line'].sudo().search([
            ('company_id', '=', self.company_id.id),
            ('date', '<=', self.date_to),
        ] + state_domain, order='account_id')
        grouped = defaultdict(lambda: {'debit': 0.0, 'credit': 0.0, 'balance': 0.0})
        accounts = {}
        for line in lines:
            code = line.account_id.code or ''
            if not code.startswith(('1', '2', '3', '4', '5')):
                continue
            accounts[line.account_id.id] = line.account_id
            grouped[line.account_id.id]['balance'] += line.balance
            if line.date >= self.date_from:
                grouped[line.account_id.id]['debit'] += line.debit
                grouped[line.account_id.id]['credit'] += line.credit
        rows = []
        for account_id in sorted(accounts, key=lambda aid: accounts[aid].code or ''):
            account = accounts[account_id]
            values = grouped[account_id]
            rows.append({
                'date': self.date_to,
                'operation': account.code,
                'document': '', 'series': '', 'partner': '', 'vat': '', 'id_type': '',
                'description': account.name,
                'quantity': 0,
                'currency': self.company_id.currency_id.name,
                'base': values['debit'], 'tax': values['credit'],
                'total': values['balance'],
                'status': 'Saldo al cierre',
                'extra': 'Clases PCGE 1 a 5; resumen de revisión',
            })
        return rows

    def _fixed_asset_rows(self):
        self.ensure_one()
        domain = [
            ('company_id', '=', self.company_id.id),
            ('move_id.move_type', 'in', ('in_invoice', 'in_refund')),
            ('move_id.invoice_date', '>=', self.date_from),
            ('move_id.invoice_date', '<=', self.date_to),
            ('account_id.code', '=like', '33%'),
            ('display_type', '=', 'product'),
        ]
        if self.target_move == 'posted':
            domain.append(('parent_state', '=', 'posted'))
        lines = self.env['account.move.line'].sudo().search(domain, order='date, move_id, id')
        rows = []
        for line in lines:
            official_number = getattr(line.move_id, 'l10n_latam_document_number', False)
            series, number = self._document_parts(
                official_number or line.move_id.name or line.move_id.ref)
            sign = -1 if line.move_id.move_type == 'in_refund' else 1
            rows.append({
                'date': line.move_id.invoice_date,
                'operation': self._document_type(line.move_id),
                'series': series, 'document': number,
                'partner': line.partner_id.display_name or '',
                'vat': line.partner_id.vat or '',
                'id_type': self._partner_id_type(line.partner_id),
                'description': line.product_id.display_name or line.name,
                'quantity': sign * line.quantity,
                'currency': line.currency_id.name or self.company_id.currency_id.name,
                'base': sign * line.price_subtotal,
                'tax': 0, 'total': sign * line.price_subtotal,
                'status': STATUS_LABELS.get(line.parent_state, line.parent_state),
                'extra': '%s · pendiente completar vida útil/depreciación' % line.account_id.code,
                'asset_code': 'AF-%06d' % line.id,
                'asset_brand': '',
                'asset_model': '',
                'asset_serial': '',
                'asset_start_date': line.move_id.invoice_date,
                'asset_method': 'Línea recta',
                'asset_rate': 0.0,
                'asset_accumulated_depreciation': 0.0,
            })
        return rows

    def _stock_domain(self):
        domain = [('company_id', '=', self.company_id.id)]
        if self.target_move == 'posted':
            domain.append(('state', '=', 'done'))
        else:
            domain.append(('state', '!=', 'cancel'))
        return domain

    def _kardex_rows(self):
        domain = self._stock_domain() + [
            ('date', '>=', fields.Datetime.to_datetime(self.date_from)),
            ('date', '<', fields.Datetime.to_datetime(self.date_to) + timedelta(days=1)),
        ]
        moves = self.env['stock.move'].sudo().search(domain, order='date, reference, id')
        rows = []
        balances = defaultdict(lambda: {'quantity': 0.0, 'value': 0.0})
        for move in moves:
            if move.location_id.usage == 'internal' and move.location_dest_id.usage != 'internal':
                direction = 'Salida'
                signed_qty = -move.quantity
            elif move.location_id.usage != 'internal' and move.location_dest_id.usage == 'internal':
                direction = 'Entrada'
                signed_qty = move.quantity
            else:
                direction = 'Transferencia'
                signed_qty = move.quantity
            value = getattr(move, 'value', 0.0) or 0.0
            balance = balances[move.product_id.id]
            entry = signed_qty if signed_qty > 0 else 0.0
            output = abs(signed_qty) if signed_qty < 0 else 0.0
            balance['quantity'] += signed_qty
            balance['value'] += value
            unit_cost = abs(value / signed_qty) if signed_qty else abs(move.price_unit or move.standard_price or 0.0)
            rows.append({
                'date': fields.Datetime.to_datetime(move.date).date(),
                'operation': direction,
                'series': move.picking_id.picking_type_id.sequence_code or '',
                'document': move.reference or move.picking_id.name or '',
                'partner': move.partner_id.display_name or '',
                'vat': move.partner_id.vat or '',
                'id_type': self._partner_id_type(move.partner_id),
                'description': move.product_id.display_name,
                'quantity': signed_qty,
                'currency': self.company_id.currency_id.name,
                'base': move.price_unit or move.standard_price or 0.0,
                'tax': 0, 'total': value,
                'status': STATUS_LABELS.get(move.state, move.state),
                'extra': '%s → %s · %s' % (
                    move.location_id.complete_name, move.location_dest_id.complete_name,
                    move.product_uom.name),
                'operation_code': {'Entrada': '02', 'Salida': '01', 'Transferencia': '12'}[direction],
                'product_code': move.product_id.default_code or '',
                'entry_quantity': entry,
                'entry_unit_cost': unit_cost if entry else 0.0,
                'output_quantity': output,
                'balance_quantity': balance['quantity'],
                'balance_value': balance['value'],
            })
        return rows

    def _guide_rows(self):
        self.ensure_one()
        date_field = 'date_done' if self.target_move == 'posted' else 'scheduled_date'
        domain = [
            ('company_id', '=', self.company_id.id),
            ('picking_type_code', 'in', ('outgoing', 'internal')),
            (date_field, '>=', fields.Datetime.to_datetime(self.date_from)),
            (date_field, '<=', fields.Datetime.to_datetime(self.date_to).replace(hour=23, minute=59, second=59)),
        ]
        domain.append(('state', '=', 'done') if self.target_move == 'posted'
                      else ('state', '!=', 'cancel'))
        pickings = self.env['stock.picking'].sudo().search(domain, order='%s, name' % date_field)
        rows = []
        for picking in pickings:
            moves = picking.move_ids.filtered(lambda move: move.state != 'cancel')
            descriptions = ', '.join(
                '%s (%s %s)' % (move.product_id.display_name, move.quantity,
                                 move.product_uom.name)
                for move in moves[:4])
            if len(moves) > 4:
                descriptions += ', y %s producto(s) más' % (len(moves) - 4)
            dt = picking.date_done or picking.scheduled_date
            rows.append({
                'date': fields.Datetime.to_datetime(dt).date() if dt else False,
                'operation': 'Salida' if picking.picking_type_code == 'outgoing' else 'Traslado interno',
                'series': picking.picking_type_id.sequence_code or '',
                'document': picking.name,
                'partner': picking.partner_id.display_name or '',
                'vat': picking.partner_id.vat or '',
                'id_type': self._partner_id_type(picking.partner_id),
                'description': descriptions,
                'quantity': sum(moves.mapped('quantity')),
                'currency': '', 'base': 0, 'tax': 0, 'total': 0,
                'status': STATUS_LABELS.get(picking.state, picking.state),
                'extra': '%s → %s · origen: %s' % (
                    picking.location_id.complete_name, picking.location_dest_id.complete_name,
                    picking.origin or '—'),
            })
        return rows

    def _warehouse_rows(self):
        self.ensure_one()
        quants = self.env['stock.quant'].sudo().search([
            ('company_id', '=', self.company_id.id),
            ('location_id.usage', '=', 'internal'),
            ('quantity', '!=', 0),
        ], order='location_id, product_id, lot_id')
        rows = []
        for quant in quants:
            value = getattr(quant, 'value', 0.0) or 0.0
            rows.append({
                'date': self.date_to,
                'operation': quant.location_id.warehouse_id.name or 'Almacén',
                'series': '', 'document': quant.lot_id.name or '',
                'partner': '', 'vat': '', 'id_type': '',
                'description': quant.product_id.display_name,
                'quantity': quant.quantity,
                'currency': self.company_id.currency_id.name,
                'base': quant.reserved_quantity,
                'tax': quant.available_quantity,
                'total': value,
                'status': 'Disponible' if quant.available_quantity > 0 else 'Reservado / sin disponible',
                'extra': '%s · %s' % (quant.location_id.complete_name, quant.product_uom_id.name),
            })
        return rows

    def _get_rows(self):
        self.ensure_one()
        self._check_company_access()
        handlers = {
            'ventas_141': lambda: self._invoice_rows(('out_invoice', 'out_refund')),
            'compras_81': lambda: self._invoice_rows(('in_invoice', 'in_refund')),
            'compras_82': lambda: self._invoice_rows(('in_invoice', 'in_refund'), non_resident=True),
            'caja_11': lambda: self._cash_bank_rows('cash'),
            'bancos_12': lambda: self._cash_bank_rows('bank'),
            'inventarios_balances': self._inventory_balance_rows,
            'activos_71': self._fixed_asset_rows,
            'kardex_131': self._kardex_rows,
            'guias': self._guide_rows,
            'almacenes': self._warehouse_rows,
            'diario_clasico': self._journal_entry_rows,
            'mayor_clasico': self._general_ledger_rows,
            'balance_comprobacion': self._trial_balance_rows,
        }
        return handlers[self.report_type]()

    def _accounting_line_domain(self, up_to_date=False):
        domain = [
            ('company_id', '=', self.company_id.id),
            ('date', '<=', self.date_to),
        ]
        if not up_to_date:
            domain.append(('date', '>=', self.date_from))
        domain.append(('parent_state', '=', 'posted') if self.target_move == 'posted'
                      else ('parent_state', 'in', ('draft', 'posted')))
        return domain

    @staticmethod
    def _tax_summary(line):
        taxes = line.tax_ids | line.tax_line_id
        return ', '.join(taxes.mapped('name'))

    def _detraction_summary(self, move):
        """Texto de control tributario, sin convertirlo en un asiento ficticio."""
        if not self.env.registry.get('pierinelli.control.tributario'):
            return ''
        detraction = self.env['pierinelli.control.tributario'].sudo().search([
            ('move_id', '=', move.id), ('tipo', '=', 'detraccion'),
        ], order='id desc', limit=1)
        if not detraction:
            return ''
        certificate = detraction.constancia or _('sin constancia')
        return _('%(rate).2f %% · %(currency)s %(amount).2f · %(certificate)s') % {
            'rate': detraction.porcentaje,
            'currency': detraction.currency_id.name,
            'amount': detraction.importe,
            'certificate': certificate,
        }

    def _accounting_row(self, line, sequence, running_balance=None):
        return {
            'sequence': sequence,
            'date': line.date,
            'operation': line.move_id.journal_id.display_name,
            'series': line.move_id.ref or '',
            'document': line.move_id.name,
            'partner': line.partner_id.display_name or '',
            'vat': line.partner_id.vat or '',
            'id_type': self._partner_id_type(line.partner_id),
            'description': line.name or '',
            'quantity': 0,
            'currency': line.company_currency_id.name,
            'base': 0,
            'tax': 0,
            'total': running_balance if running_balance is not None else line.balance,
            'debit': line.debit,
            'credit': line.credit,
            'balance': running_balance if running_balance is not None else line.balance,
            'tax_info': self._tax_summary(line),
            # El impuesto se muestra una sola vez: en la línea tributaria que
            # Odoo generó. Repetirlo en cada base imponible duplicaría el IGV.
            'tax_amount': abs(line.balance) if line.tax_line_id else 0.0,
            'tax_account': ('%s %s' % (line.account_id.code or '', line.account_id.name or '')
                            if line.tax_line_id else ''),
            'detraction_info': '',
            'status': STATUS_LABELS.get(line.parent_state, line.parent_state),
            'extra': '%s %s' % (line.account_id.code or '', line.account_id.name or ''),
            'account_code': line.account_id.code or '',
            'account_name': line.account_id.name or '',
        }

    def _journal_entry_rows(self):
        lines = self.env['account.move.line'].sudo().search(
            self._accounting_line_domain(), order='date, move_id, sequence, id')
        rows = []
        previous_move_id = None
        for line in lines:
            if line.display_type in ('line_section', 'line_note'):
                continue
            is_start = line.move_id.id != previous_move_id
            previous_move_id = line.move_id.id
            row = self._accounting_row(line, len(rows) + 1)
            row.update({
                'entry_start': is_start,
                'entry_total': sum(line.move_id.line_ids.mapped('debit')),
                'detraction_info': self._detraction_summary(line.move_id) if is_start else '',
            })
            rows.append(row)
        return rows

    def _opening_balance_by_account(self, account_ids=None):
        domain = self._accounting_line_domain(up_to_date=True) + [
            ('date', '<', self.date_from),
        ]
        if account_ids:
            domain.append(('account_id', 'in', account_ids))
        lines = self.env['account.move.line'].sudo().search(domain)
        opening = defaultdict(float)
        for line in lines:
            if line.display_type not in ('line_section', 'line_note'):
                opening[line.account_id.id] += line.debit - line.credit
        return opening

    @staticmethod
    def _debit_credit_from_balance(balance):
        return max(balance, 0.0), max(-balance, 0.0)

    def _general_ledger_rows(self):
        domain = self._accounting_line_domain()
        if self.account_id:
            domain.append(('account_id', '=', self.account_id.id))
        lines = self.env['account.move.line'].sudo().search(
            domain, order='account_id, date, move_id, id')
        account_ids = lines.account_id.ids or self.account_id.ids
        balances = self._opening_balance_by_account(account_ids)
        rows = []
        accounts = self.env['account.account'].browse(account_ids).sorted(
            key=lambda account: account.code or '')
        for account in accounts:
            opening = balances[account.id]
            opening_debit, opening_credit = self._debit_credit_from_balance(opening)
            rows.append({
                'sequence': len(rows) + 1, 'date': self.date_from,
                'operation': _('Saldo anterior'), 'series': '', 'document': '',
                'partner': '', 'vat': '', 'id_type': '',
                'description': _('Saldo anterior'), 'quantity': 0,
                'currency': self.company_id.currency_id.name,
                'base': 0, 'tax': 0, 'total': opening,
                'debit': 0, 'credit': 0, 'balance': opening,
                'balance_debit': opening_debit, 'balance_credit': opening_credit,
                'tax_info': '', 'status': '',
                'extra': '%s %s' % (account.code or '', account.name or ''),
                'account_code': account.code or '', 'account_name': account.name or '',
                'entry_start': True,
            })
            for line in lines.filtered(lambda move_line: move_line.account_id == account):
                if line.display_type in ('line_section', 'line_note'):
                    continue
                balances[account.id] += line.debit - line.credit
                balance_debit, balance_credit = self._debit_credit_from_balance(balances[account.id])
                row = self._accounting_row(line, len(rows) + 1, balances[account.id])
                row.update({
                    'opening_balance': balances[account.id] - line.debit + line.credit,
                    'balance_debit': balance_debit,
                    'balance_credit': balance_credit,
                })
                rows.append(row)
        self._set_mayor_summary(lines, balances)
        return rows

    def _set_mayor_summary(self, lines, balances):
        if self.account_id:
            account = self.account_id
            opening = self._opening_balance_by_account(account.ids).get(account.id, 0.0)
            debit = sum(lines.filtered(lambda line: line.account_id == account).mapped('debit'))
            credit = sum(lines.filtered(lambda line: line.account_id == account).mapped('credit'))
            closing = opening + debit - credit
            label = '%s %s' % (account.code or '', account.name or '')
        else:
            opening_by_account = self._opening_balance_by_account(lines.account_id.ids)
            opening = sum(opening_by_account.values())
            debit = sum(lines.mapped('debit'))
            credit = sum(lines.mapped('credit'))
            closing = opening + debit - credit
            label = _('Todas las cuentas · seleccione una cuenta para análisis individual')
        opening_debit, opening_credit = self._debit_credit_from_balance(opening)
        closing_debit, closing_credit = self._debit_credit_from_balance(closing)
        self.mayor_summary = label
        self.mayor_opening_debit = opening_debit
        self.mayor_opening_credit = opening_credit
        self.mayor_movement_debit = debit
        self.mayor_movement_credit = credit
        self.mayor_closing_debit = closing_debit
        self.mayor_closing_credit = closing_credit

    def _trial_balance_rows(self):
        lines = self.env['account.move.line'].sudo().search(
            self._accounting_line_domain(up_to_date=True), order='account_id, date, id')
        grouped = defaultdict(lambda: {
            'opening': 0.0, 'debit': 0.0, 'credit': 0.0, 'balance': 0.0})
        accounts = {}
        for line in lines:
            if line.display_type in ('line_section', 'line_note'):
                continue
            accounts[line.account_id.id] = line.account_id
            if line.date >= self.date_from:
                grouped[line.account_id.id]['debit'] += line.debit
                grouped[line.account_id.id]['credit'] += line.credit
            else:
                grouped[line.account_id.id]['opening'] += line.debit - line.credit
            grouped[line.account_id.id]['balance'] += line.debit - line.credit
        rows = []
        for account_id in sorted(accounts, key=lambda acc_id: accounts[acc_id].code or ''):
            account = accounts[account_id]
            values = grouped[account_id]
            opening_debit, opening_credit = self._debit_credit_from_balance(values['opening'])
            closing_debit, closing_credit = self._debit_credit_from_balance(values['balance'])
            rows.append({
                'sequence': len(rows) + 1,
                'date': self.date_to,
                'operation': 'Balance de comprobación',
                'series': '', 'document': '', 'partner': '', 'vat': '', 'id_type': '',
                'description': account.name,
                'quantity': 0, 'currency': self.company_id.currency_id.name,
                'base': 0, 'tax': 0, 'total': values['balance'],
                'debit': values['debit'], 'credit': values['credit'],
                'balance': values['balance'],
                'opening_debit': opening_debit, 'opening_credit': opening_credit,
                'closing_debit': closing_debit, 'closing_credit': closing_credit,
                'tax_info': '',
                'status': 'Saldo al cierre',
                'extra': account.code or '',
            })
        return rows

    def action_prepare(self):
        self.ensure_one()
        rows = self._get_rows()
        commands = [Command.clear()]
        for sequence, row in enumerate(rows, 1):
            commands.append(Command.create(dict(row, sequence=sequence)))
        self.write({
            'line_ids': commands,
            'prepared': True,
            'export_file': False,
            'export_filename': False,
            'preview_note': self._empty_message() if not rows else False,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _empty_message(self):
        self.ensure_one()
        if self.report_type == 'compras_82':
            return _(
                'No hay compras no domiciliadas en el periodo. Para aparecer en 8.2, '
                'la factura debe ser de proveedor y su país debe ser distinto de Perú.')
        if self.report_type in ACCOUNTING_REPORT_TYPES:
            return _('No hay apuntes contables en el periodo y estado seleccionados.')
        return _('No hay registros para los filtros seleccionados. Ajuste el periodo o incluya borradores.')

    def action_show_format_help(self):
        self.ensure_one()
        help_record = self.env['pierinelli.libros.sire.help'].create({})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Información de formatos'),
            'res_model': 'pierinelli.libros.sire.help',
            'res_id': help_record.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _ensure_prepared(self):
        self.ensure_one()
        if not self.prepared:
            self.action_prepare()

    def _export_headers(self):
        if self.report_type in ACCOUNTING_REPORT_TYPES:
            return [
                'N°', 'Fecha', 'Diario', 'Asiento', 'Cuenta contable',
                'Tercero', 'Glosa / descripción', 'Impuestos', 'Debe',
                'Haber', 'Saldo', 'Estado', 'Referencia',
            ]
        return [
            'N°', 'Fecha', 'Tipo/operación', 'Serie', 'Número', 'Proveedor / cliente',
            'Tipo doc. identidad', 'RUC / documento', 'Producto / concepto', 'Cantidad',
            'Moneda', 'Base / débito', 'IGV / crédito', 'Total / saldo', 'Estado', 'Referencia',
        ]

    def _excel_layout(self):
        """Encabezados y orden de columnas basados en los formatos entregados."""
        layouts = {
            'ventas_141': (
                'FORMATO 14.1: REGISTRO DE VENTAS E INGRESOS ELECTRÓNICOS (RVIE)',
                ['N° Correlativo', 'Fecha Emisión', 'Tipo Doc (Tabla 10)', 'Serie', 'Número',
                 'Tipo Doc Ident', 'N° Doc Cliente', 'Razón Social Cliente',
                 'Base Imponible Gravada', 'IGV', 'Monto Total', 'Moneda', 'Estado SUNAT'],
                [15, 14, 18, 12, 14, 16, 18, 36, 22, 14, 18, 12, 18],
                (8, 9, 10), self._excel_sales_values),
            'compras_81': (
                'FORMATO 8.1: REGISTRO DE COMPRAS ELECTRÓNICO (RCE - DOMICILIADOS)',
                ['Periodo/CUO', 'Fecha Emisión', 'Tipo Doc', 'Serie', 'Número',
                 'Tipo Doc Prov', 'RUC Proveedor', 'Razón Social Proveedor',
                 'BI Compras Gravadas', 'IGV', 'Otros Tributos', 'Monto Total',
                 'Moneda', 'Constancia Detracción'],
                [16, 14, 11, 12, 14, 15, 18, 36, 22, 14, 16, 18, 12, 22],
                (8, 9, 10, 11), self._excel_purchase_values),
            'compras_82': (
                'FORMATO 8.2: REGISTRO DE COMPRAS - OPERACIONES CON NO DOMICILIADOS',
                ['Periodo/CUO', 'Fecha Emisión', 'Tipo Doc', 'Serie', 'Número',
                 'Tipo Doc Prov', 'Doc. Proveedor', 'Razón Social Proveedor',
                 'BI Compras Gravadas', 'IGV', 'Otros Tributos', 'Monto Total',
                 'Moneda', 'Referencia'],
                [16, 14, 11, 12, 14, 15, 20, 36, 22, 14, 16, 18, 12, 28],
                (8, 9, 10, 11), self._excel_purchase_values),
            'activos_71': (
                'FORMATO 7.1: REGISTRO DE ACTIVOS FIJOS',
                ['Código Activo', 'Descripción del Activo', 'Marca', 'Modelo', 'N° Serie',
                 'Fecha Adquisición', 'Fecha Inicio Uso', 'Método Deprec.', 'Tasa %',
                 'Valor Adquisición', 'Depreciación Acum.'],
                [16, 38, 18, 18, 18, 16, 16, 18, 12, 20, 22],
                (9, 10), self._excel_asset_values),
            'kardex_131': (
                'FORMATO 13.1: REGISTRO DE INVENTARIO PERMANENTE VALORIZADO (KARDEX)',
                ['Fecha', 'Tipo Doc', 'Serie-Número', 'Tipo Operación', 'Cod. Producto',
                 'Descripción', 'Entrada Cant.', 'Costo Unit. Ent.', 'Salida Cant.',
                 'Saldo Cantid.', 'Costo Total Saldo'],
                [14, 12, 20, 16, 20, 38, 16, 18, 16, 16, 20],
                (6, 7, 8, 9, 10), self._excel_kardex_values),
            'diario_clasico': (
                'LIBRO DIARIO CLÁSICO - ASIENTOS DEBE Y HABER',
                ['N° Asiento', 'Fecha', 'Contacto / contraparte', 'Glosa / Descripción',
                 'Cuenta Contable', 'Denominación Cuenta', 'Debe (S/.)', 'Haber (S/.)',
                 'Impuesto aplicado', 'Importe impuesto (S/.)', 'Cuenta de impuesto',
                 'Detracción / constancia', 'Suma Asiento'],
                [16, 14, 30, 42, 18, 32, 18, 18, 22, 22, 32, 32, 18],
                (6, 7, 9, 12), self._excel_journal_values),
            'mayor_clasico': (
                'LIBRO MAYOR CLÁSICO - MOVIMIENTOS Y SALDOS',
                ['Cuenta Contable', 'Fecha', 'N° Asiento', 'Glosa / Descripción',
                 'Debe (S/.)', 'Haber (S/.)', 'Saldo Deudor', 'Saldo Acreedor'],
                [30, 14, 18, 45, 18, 18, 18, 18],
                (4, 5, 6, 7), self._excel_ledger_values),
            'balance_comprobacion': (
                'BALANCE DE COMPROBACIÓN - SUMAS Y SALDOS',
                ['Cuenta Contable', 'Denominación Cuenta', 'Saldo Inicial Deudor',
                 'Saldo Inicial Acreedor', 'Movimientos Debe', 'Movimientos Haber',
                 'Saldo Final Deudor', 'Saldo Final Acreedor'],
                [18, 36, 20, 20, 18, 18, 20, 20],
                (2, 3, 4, 5, 6, 7), self._excel_trial_balance_values),
        }
        if self.report_type in layouts:
            return layouts[self.report_type]
        headers = self._export_headers()
        numeric = ((8, 9, 10) if self.report_type in ACCOUNTING_REPORT_TYPES
                   else (9, 11, 12, 13))
        return self._report_label(), headers, [18] * len(headers), numeric, self._export_values

    @staticmethod
    def _date_value(value):
        return value or ''

    def _excel_sales_values(self, line):
        return [line.correlative, self._date_value(line.date), line.operation, line.series,
                line.document, line.id_type, line.vat, line.partner, line.base,
                line.tax, line.total, line.currency, line.status]

    def _excel_purchase_values(self, line):
        last_value = line.detraction if self.report_type == 'compras_81' else line.extra
        return [line.cuo, self._date_value(line.date), line.operation, line.series,
                line.document, line.id_type, line.vat, line.partner, line.base,
                line.tax, line.other_tax, line.total, line.currency, last_value]

    def _excel_asset_values(self, line):
        return [line.asset_code, line.description, line.asset_brand, line.asset_model,
                line.asset_serial, self._date_value(line.date),
                self._date_value(line.asset_start_date), line.asset_method,
                line.asset_rate / 100 if line.asset_rate else 0.0, line.base,
                line.asset_accumulated_depreciation]

    def _excel_kardex_values(self, line):
        return [self._date_value(line.date), '00', line.document,
                line.operation_code, line.product_code, line.description,
                line.entry_quantity, line.entry_unit_cost, line.output_quantity,
                line.balance_quantity, line.balance_value]

    def _excel_journal_values(self, line):
        return [line.document, self._date_value(line.date), line.partner,
                line.description, line.account_code, line.account_name, line.debit,
                line.credit, line.tax_info, line.tax_amount, line.tax_account,
                line.detraction_info, line.entry_total]

    def _excel_ledger_values(self, line):
        return [line.extra, self._date_value(line.date), line.document,
                line.description, line.debit, line.credit, line.balance_debit,
                line.balance_credit]

    def _excel_trial_balance_values(self, line):
        return [line.extra, line.description, line.opening_debit, line.opening_credit,
                line.debit, line.credit, line.closing_debit, line.closing_credit]

    def _export_values(self, line):
        if self.report_type in ACCOUNTING_REPORT_TYPES:
            return [
                line.sequence, line.date, line.operation, line.document, line.extra,
                line.partner, line.description, line.tax_info, line.debit,
                line.credit, line.balance, line.status, line.series,
            ]
        return [
            line.sequence, line.date, line.operation, line.series, line.document,
            line.partner, line.id_type, line.vat, line.description, line.quantity,
            line.currency, line.base, line.tax, line.total, line.status, line.extra,
        ]

    def _filename_base(self):
        return '%s_%s_%s' % (
            self.report_type.upper(), self.date_from.strftime('%Y%m%d'),
            self.date_to.strftime('%Y%m%d'))

    def _download_action(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=%s&id=%s&field=export_file&filename_field=export_filename&download=true&filename=%s'
                   % (self._name, self.id, quote(self.export_filename or 'reporte')),
            'target': 'self',
        }

    def action_export_xlsx(self):
        self._ensure_prepared()
        if xlsxwriter is None:
            raise UserError(_('No está instalada la librería xlsxwriter en el servidor.'))
        stream = io.BytesIO()
        workbook = xlsxwriter.Workbook(stream, {'in_memory': True})
        title_text, headers, widths, number_columns, values_getter = self._excel_layout()
        sheet = workbook.add_worksheet('Reporte')
        dictionary = workbook.add_worksheet('Información')
        title = workbook.add_format({
            'bold': True, 'font_size': 16, 'font_color': '#FFFFFF',
            'bg_color': '#111111', 'align': 'left'})
        gold = workbook.add_format({'bold': True, 'bg_color': '#C9962F', 'border': 1})
        sample_header = workbook.add_format({
            'bold': True, 'font_color': '#FFFFFF', 'bg_color': '#1F4E78',
            'border': 1, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        text_format = workbook.add_format({'border': 1, 'valign': 'top'})
        date_format = workbook.add_format({'border': 1, 'num_format': 'dd/mm/yyyy'})
        number_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
        last_col = len(headers) - 1
        sheet.merge_range(0, 0, 0, last_col, title_text, title)
        sheet.write(1, 0, 'Empresa', gold)
        sheet.write(1, 1, self.company_id.display_name)
        sheet.write(1, 3, 'RUC', gold)
        sheet.write(1, 4, self.company_id.vat or '')
        sheet.write(1, 6, 'Periodo', gold)
        sheet.write(1, 7, '%s al %s' % (
            self.date_from.strftime('%d/%m/%Y'), self.date_to.strftime('%d/%m/%Y')))
        for col, label in enumerate(headers):
            sheet.write(3, col, label, sample_header)
        for row_idx, line in enumerate(self.line_ids, 4):
            for col_idx, value in enumerate(values_getter(line)):
                cell_format = text_format
                if col_idx == 1 and value:
                    cell_format = date_format
                elif col_idx in number_columns:
                    cell_format = number_format
                is_number = col_idx in number_columns
                sheet.write(row_idx, col_idx, value or 0 if is_number else value or '', cell_format)
        sheet.freeze_panes(4, 0)
        sheet.autofilter(3, 0, max(3, 3 + len(self.line_ids)), last_col)
        for col, width in enumerate(widths):
            sheet.set_column(col, col, width)

        dictionary.write(0, 0, 'Información', gold)
        dictionary.write(0, 1, 'Detalle', gold)
        pipeline = [
            ('Fuente', 'Información generada desde operaciones y asientos registrados en el ERP.'),
            ('Formato', 'Columnas organizadas según la estructura de referencia entregada.'),
            ('TXT', 'Archivo de demostración con nomenclatura PLE de 33 caracteres.'),
        ]
        for idx, values in enumerate(pipeline, 1):
            dictionary.write(idx, 0, values[0], text_format)
            dictionary.write(idx, 1, values[1], text_format)
        dictionary.write(6, 0, 'Campo', gold)
        dictionary.write(6, 1, 'Contenido', gold)
        for idx, label in enumerate(headers, 7):
            dictionary.write(idx, 0, label, text_format)
            dictionary.write(idx, 1, 'Dato generado desde la operación o asiento correspondiente.', text_format)
        dictionary.set_column(0, 0, 25)
        dictionary.set_column(1, 1, 85)
        workbook.close()
        filename = '%s_REVISION.xlsx' % self._filename_base()
        self.write({'export_file': base64.b64encode(stream.getvalue()), 'export_filename': filename})
        return self._download_action()

    @staticmethod
    def _txt_value(value):
        if isinstance(value, date):
            value = value.strftime('%d/%m/%Y')
        elif isinstance(value, float):
            value = '%.2f' % value
        return str(value or '').replace('|', '/').replace('\r', ' ').replace('\n', ' ')

    def action_export_txt(self):
        self._ensure_prepared()
        _title, _headers, _widths, _numbers, values_getter = self._excel_layout()
        # PLE trabaja sin fila de encabezado y con campos separados por pipe.
        # El contenido es una demostración estructurada para el flujo comercial;
        # la homologación final se realiza con la estructura SUNAT vigente.
        lines = ['|'.join(self._txt_value(value) for value in values_getter(line))
                 for line in self.line_ids]
        payload = '\r\n'.join(lines) + '\r\n'
        filename = self._ple_filename()
        self.write({
            'export_file': base64.b64encode(payload.encode('utf-8-sig')),
            'export_filename': filename,
        })
        return self._download_action()

    def _ple_filename(self):
        """Nombre PLE de 33 caracteres previos a la extensión .txt."""
        self.ensure_one()
        book_code = {
            'caja_11': '0101', 'bancos_12': '0102',
            'inventarios_balances': '0301', 'diario_clasico': '0501',
            'mayor_clasico': '0601', 'activos_71': '0701',
            'compras_81': '0801', 'compras_82': '0802',
            'kardex_131': '1301', 'ventas_141': '1401',
        }.get(self.report_type, '0000')
        ruc = ''.join(char for char in (self.company_id.vat or '') if char.isdigit())
        ruc = (ruc + '0' * 11)[:11]
        base = 'LE%s%s00%s00001111' % (
            ruc, self.date_to.strftime('%Y%m'), book_code)
        if len(base) != 33:
            raise UserError(_('No se pudo construir la nomenclatura PLE de 33 caracteres.'))
        return '%s.txt' % base

    def action_export_pdf(self):
        self._ensure_prepared()
        return self.env.ref('pierinelli_reportes.action_report_libros_sire').report_action(self)

    def get_report_payload(self):
        self.ensure_one()
        title, headers, _widths, number_columns, values_getter = self._excel_layout()
        return {
            'title': title,
            'company': self.company_id.display_name,
            'vat': self.company_id.vat or '',
            'period': '%s al %s' % (
                self.date_from.strftime('%d/%m/%Y'), self.date_to.strftime('%d/%m/%Y')),
            'headers': headers,
            'rows': [values_getter(line) for line in self.line_ids],
            'number_columns': number_columns,
            'total_label': 'TOTALES DE CONTROL',
            'total_values': self._pdf_total_values(headers, number_columns),
            'totals': {
                'quantity': sum(self.line_ids.mapped('quantity')),
                'base': sum(self.line_ids.mapped('base')),
                'tax': sum(self.line_ids.mapped('tax')),
                'total': sum(self.line_ids.mapped('total')),
                'debit': sum(self.line_ids.mapped('debit')),
                'credit': sum(self.line_ids.mapped('credit')),
                'balance': sum(self.line_ids.mapped('balance')),
            },
        }

    def _pdf_total_values(self, headers, number_columns):
        values = [''] * len(headers)
        values[0] = 'TOTALES DE CONTROL'
        mapping = {
            'ventas_141': {8: 'base', 9: 'tax', 10: 'total'},
            'compras_81': {8: 'base', 9: 'tax', 10: 'other_tax', 11: 'total'},
            'compras_82': {8: 'base', 9: 'tax', 10: 'other_tax', 11: 'total'},
            'activos_71': {9: 'base', 10: 'asset_accumulated_depreciation'},
            'diario_clasico': {6: 'debit', 7: 'credit', 9: 'tax_amount'},
            'mayor_clasico': {4: 'debit', 5: 'credit', 6: 'balance_debit', 7: 'balance_credit'},
            'balance_comprobacion': {
                2: 'opening_debit', 3: 'opening_credit', 4: 'debit', 5: 'credit',
                6: 'closing_debit', 7: 'closing_credit'},
        }
        for index, field_name in mapping.get(self.report_type, {}).items():
            values[index] = sum(self.line_ids.mapped(field_name))
        return values


class LibrosSireLine(models.TransientModel):
    _name = 'pierinelli.libros.sire.line'
    _description = 'Línea de vista previa de libro'
    _order = 'sequence, id'

    wizard_id = fields.Many2one(
        'pierinelli.libros.sire.wizard', required=True, ondelete='cascade')
    sequence = fields.Integer(string='N°')
    date = fields.Date(string='Fecha')
    operation = fields.Char(string='Tipo / operación')
    series = fields.Char(string='Serie')
    document = fields.Char(string='Número')
    partner = fields.Char(string='Proveedor / cliente')
    id_type = fields.Char(string='Tipo doc.')
    vat = fields.Char(string='RUC / documento')
    description = fields.Char(string='Producto / concepto')
    quantity = fields.Float(string='Cantidad')
    currency = fields.Char(string='Moneda')
    base = fields.Float(string='Base / débito')
    tax = fields.Float(string='IGV / crédito')
    total = fields.Float(string='Total / saldo')
    status = fields.Char(string='Estado')
    extra = fields.Char(string='Referencia')
    debit = fields.Float(string='Debe')
    credit = fields.Float(string='Haber')
    balance = fields.Float(string='Saldo')
    tax_info = fields.Char(string='Impuestos')
    tax_amount = fields.Float(string='Importe de impuesto')
    tax_account = fields.Char(string='Cuenta de impuesto')
    detraction_info = fields.Char(string='Detracción / constancia')
    account_code = fields.Char(string='Código de cuenta')
    account_name = fields.Char(string='Denominación de cuenta')
    entry_start = fields.Boolean(string='Inicio de asiento')
    entry_total = fields.Float(string='Suma del asiento')
    opening_balance = fields.Float(string='Saldo anterior')
    opening_debit = fields.Float(string='Saldo inicial deudor')
    opening_credit = fields.Float(string='Saldo inicial acreedor')
    closing_debit = fields.Float(string='Saldo final deudor')
    closing_credit = fields.Float(string='Saldo final acreedor')
    balance_debit = fields.Float(string='Saldo deudor')
    balance_credit = fields.Float(string='Saldo acreedor')
    correlative = fields.Char(string='Correlativo')
    cuo = fields.Char(string='CUO')
    other_tax = fields.Float(string='Otros tributos')
    detraction = fields.Char(string='Constancia detracción')
    asset_code = fields.Char(string='Código activo')
    asset_brand = fields.Char(string='Marca activo')
    asset_model = fields.Char(string='Modelo activo')
    asset_serial = fields.Char(string='Serie activo')
    asset_start_date = fields.Date(string='Inicio de uso')
    asset_method = fields.Char(string='Método depreciación')
    asset_rate = fields.Float(string='Tasa depreciación')
    asset_accumulated_depreciation = fields.Float(string='Depreciación acumulada')
    operation_code = fields.Char(string='Código operación')
    product_code = fields.Char(string='Código producto')
    entry_quantity = fields.Float(string='Cantidad entrada')
    entry_unit_cost = fields.Float(string='Costo unitario entrada')
    output_quantity = fields.Float(string='Cantidad salida')
    balance_quantity = fields.Float(string='Saldo cantidad')
    balance_value = fields.Float(string='Saldo valorizado')


class LibrosSireHelp(models.TransientModel):
    _name = 'pierinelli.libros.sire.help'
    _description = 'Ayuda de formatos de libros y SIRE'

    content = fields.Html(
        string='Información', readonly=True, sanitize=False,
        default=lambda self: _(
            '<p>Este centro organiza la información contable y operativa para su revisión, '
            'presentación y exportación.</p>'
            '<ul>'
            '<li><strong>8.1</strong>: compras de proveedores domiciliados.</li>'
            '<li><strong>8.2</strong>: compras a proveedores no domiciliados.</li>'
            '<li><strong>14.1</strong>: ventas e ingresos.</li>'
            '<li><strong>7.1</strong>: activos fijos.</li>'
            '<li><strong>3.x</strong>: Inventarios y Balances.</li>'
            '</ul>'
            '<p>La revisión y las exportaciones se realizan desde este sistema. '
            'La presentación oficial se habilita al completar la integración y validación SUNAT.</p>'))

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}
