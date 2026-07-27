# -*- coding: utf-8 -*-
"""
Motor de estados financieros para Pierinelli (Odoo Community).

Odoo Community NO trae los reportes financieros con formato oficial (son de
Enterprise). Aqui los construimos leyendo directamente de account.move.line y
agrupando por la estructura del Plan Contable General Empresarial (PCGE) peruano,
que clasifica las cuentas por su primer digito:

    1  Activo disponible y exigible / realizable
    2  Activo realizable (existencias)
    3  Activo inmovilizado (activo no corriente)
    4  Pasivo (obligaciones, tributos, cuentas por pagar)
    5  Patrimonio
    6  Gastos por naturaleza
    7  Ingresos
    8  Saldos intermediarios de gestion
    9  Contabilidad analitica de explotacion
    0  Cuentas de orden

El Balance se arma con clases 1,2,3 (activo), 4 (pasivo), 5 (patrimonio) y el
resultado del ejercicio (7 - 6). El Estado de Resultados con clases 7 (ingresos)
y 6 (gastos).
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class FinancialReportWizard(models.TransientModel):
    _name = 'pierinelli.financial.report.wizard'
    _description = 'Asistente de Estados Financieros Pierinelli'

    date_from = fields.Date(
        string='Desde',
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(month=1, day=1),
    )
    date_to = fields.Date(
        string='Hasta',
        required=True,
        default=fields.Date.context_today,
    )
    target_move = fields.Selection(
        [('posted', 'Solo asientos publicados'),
         ('all', 'Todos (incluye borradores)')],
        string='Asientos',
        default='posted',
        required=True,
    )
    company_id = fields.Many2one(
        'res.company', string='Compania', required=True,
        default=lambda self: self.env.company,
    )

    # ------------------------------------------------------------------
    #  Utilidades de consulta
    # ------------------------------------------------------------------
    def _base_domain(self, only_dates_to=False):
        """Dominio comun sobre account.move.line."""
        domain = [('company_id', '=', self.company_id.id)]
        if self.target_move == 'posted':
            domain.append(('parent_state', '=', 'posted'))
        else:
            domain.append(('parent_state', 'in', ('posted', 'draft')))
        if only_dates_to:
            # Balance: saldo acumulado hasta la fecha (cuentas de situacion)
            domain.append(('date', '<=', self.date_to))
        else:
            domain += [('date', '>=', self.date_from),
                       ('date', '<=', self.date_to)]
        return domain

    def _balance_by_account(self, domain):
        """Devuelve {account_id: {'code','name','debit','credit','balance'}}."""
        Line = self.env['account.move.line']
        groups = Line.read_group(
            domain,
            ['debit:sum', 'credit:sum', 'balance:sum'],
            ['account_id'],
        )
        result = {}
        for g in groups:
            if not g.get('account_id'):
                continue
            acc_id = g['account_id'][0]
            acc = self.env['account.account'].browse(acc_id)
            result[acc_id] = {
                'id': acc_id,
                'code': acc.code or '',
                'name': acc.name or '',
                'debit': g.get('debit') or 0.0,
                'credit': g.get('credit') or 0.0,
                'balance': g.get('balance') or 0.0,
            }
        return result

    @staticmethod
    def _pcge_class(code):
        """Primer digito significativo del codigo PCGE."""
        code = (code or '').strip()
        return code[0] if code else ''

    # ------------------------------------------------------------------
    #  Formateo: los montos se convierten a texto EN PYTHON y se guardan en
    #  claves con sufijo "_s". QWeb no permite str.format() ni funciones
    #  arbitrarias dentro del render de web.external_layout, asi que todo lo
    #  numerico que se muestra ya viene formateado como cadena.
    # ------------------------------------------------------------------
    @staticmethod
    def _money(value):
        try:
            return '{:,.2f}'.format(value or 0.0)
        except (ValueError, TypeError):
            return '0.00'

    @staticmethod
    def _money0(value):
        try:
            return '{:,.0f}'.format(value or 0.0)
        except (ValueError, TypeError):
            return '0'

    @classmethod
    def _fmt_rows(cls, rows, keys):
        """Agrega 'k_s' (string) por cada clave numerica k de cada fila."""
        for r in rows:
            for k in keys:
                r[k + '_s'] = cls._money(r.get(k, 0.0))
        return rows

    # ------------------------------------------------------------------
    #  Estado de Situacion Financiera (Balance General)
    # ------------------------------------------------------------------
    def _compute_financial_position(self):
        data = self._balance_by_account(self._base_domain(only_dates_to=True))

        activo, pasivo, patrimonio = [], [], []
        total_activo = total_pasivo = total_patrimonio = 0.0
        resultado_ejercicio = 0.0

        for acc in data.values():
            cls = self._pcge_class(acc['code'])
            bal = acc['balance']
            if cls in ('1', '2', '3'):
                acc['monto'] = bal            # activo: saldo deudor positivo
                activo.append(acc)
                total_activo += bal
            elif cls == '4':
                acc['monto'] = -bal           # pasivo: saldo acreedor -> positivo
                pasivo.append(acc)
                total_pasivo += -bal
            elif cls == '5':
                acc['monto'] = -bal           # patrimonio: acreedor -> positivo
                patrimonio.append(acc)
                total_patrimonio += -bal
            elif cls in ('6', '7'):
                # resultado del ejercicio = ingresos(7) - gastos(6)
                resultado_ejercicio += -bal

        # El resultado del ejercicio integra el patrimonio
        total_patrimonio += resultado_ejercicio

        activo.sort(key=lambda a: a['code'])
        pasivo.sort(key=lambda a: a['code'])
        patrimonio.sort(key=lambda a: a['code'])
        self._fmt_rows(activo, ['monto'])
        self._fmt_rows(pasivo, ['monto'])
        self._fmt_rows(patrimonio, ['monto'])

        descuadre = total_activo - (total_pasivo + total_patrimonio)
        return {
            'activo': activo,
            'pasivo': pasivo,
            'patrimonio': patrimonio,
            'resultado_ejercicio': resultado_ejercicio,
            'resultado_ejercicio_s': self._money(resultado_ejercicio),
            'total_activo': total_activo,
            'total_activo_s': self._money(total_activo),
            'total_pasivo': total_pasivo,
            'total_pasivo_s': self._money(total_pasivo),
            'total_patrimonio': total_patrimonio,
            'total_patrimonio_s': self._money(total_patrimonio),
            'total_pasivo_patrimonio': total_pasivo + total_patrimonio,
            'total_pasivo_patrimonio_s': self._money(total_pasivo + total_patrimonio),
            'descuadre': descuadre,
            'descuadre_s': self._money(descuadre),
        }

    # ------------------------------------------------------------------
    #  Estado de Resultados (Ganancias y Perdidas)
    # ------------------------------------------------------------------
    def _compute_income_statement(self):
        data = self._balance_by_account(self._base_domain())

        ingresos, gastos = [], []
        total_ingresos = total_gastos = 0.0

        for acc in data.values():
            cls = self._pcge_class(acc['code'])
            bal = acc['balance']
            if cls == '7':
                acc['monto'] = -bal           # ingreso: acreedor -> positivo
                ingresos.append(acc)
                total_ingresos += -bal
            elif cls == '6':
                acc['monto'] = bal            # gasto: deudor -> positivo
                gastos.append(acc)
                total_gastos += bal

        ingresos.sort(key=lambda a: a['code'])
        gastos.sort(key=lambda a: a['code'])
        self._fmt_rows(ingresos, ['monto'])
        self._fmt_rows(gastos, ['monto'])

        utilidad_bruta = total_ingresos - total_gastos
        # IGV no entra aqui (es cuenta 40 del pasivo). Impuesto a la renta
        # estimado 29.5% sobre utilidad positiva (referencial).
        impuesto_renta = utilidad_bruta * 0.295 if utilidad_bruta > 0 else 0.0
        utilidad_neta = utilidad_bruta - impuesto_renta
        margen = (utilidad_bruta / total_ingresos * 100.0) if total_ingresos else 0.0

        return {
            'ingresos': ingresos,
            'gastos': gastos,
            'total_ingresos': total_ingresos,
            'total_ingresos_s': self._money(total_ingresos),
            'total_ingresos_s0': self._money0(total_ingresos),
            'total_gastos': total_gastos,
            'total_gastos_s': self._money(total_gastos),
            'total_gastos_s0': self._money0(total_gastos),
            'utilidad_bruta': utilidad_bruta,
            'utilidad_bruta_s': self._money(utilidad_bruta),
            'impuesto_renta': impuesto_renta,
            'impuesto_renta_s': self._money(impuesto_renta),
            'utilidad_neta': utilidad_neta,
            'utilidad_neta_s': self._money(utilidad_neta),
            'utilidad_neta_s0': self._money0(utilidad_neta),
            'margen': margen,
            'margen_s': '{:,.1f}%'.format(margen),
        }

    # ------------------------------------------------------------------
    #  Balance de Comprobacion (sumas y saldos)
    # ------------------------------------------------------------------
    def _compute_trial_balance(self):
        data = self._balance_by_account(self._base_domain())
        rows = sorted(data.values(), key=lambda a: a['code'])
        for r in rows:
            r['saldo_deudor'] = r['balance'] if r['balance'] > 0 else 0.0
            r['saldo_acreedor'] = -r['balance'] if r['balance'] < 0 else 0.0
        self._fmt_rows(rows, ['debit', 'credit', 'saldo_deudor', 'saldo_acreedor'])
        total_debit = sum(r['debit'] for r in rows)
        total_credit = sum(r['credit'] for r in rows)
        total_deudor = sum(r['saldo_deudor'] for r in rows)
        total_acreedor = sum(r['saldo_acreedor'] for r in rows)
        return {
            'rows': rows,
            'total_debit': total_debit,
            'total_debit_s': self._money(total_debit),
            'total_credit': total_credit,
            'total_credit_s': self._money(total_credit),
            'total_deudor': total_deudor,
            'total_deudor_s': self._money(total_deudor),
            'total_acreedor': total_acreedor,
            'total_acreedor_s': self._money(total_acreedor),
        }

    # ------------------------------------------------------------------
    #  Libro Mayor (detalle de movimientos por cuenta)
    # ------------------------------------------------------------------
    def _compute_general_ledger(self):
        Line = self.env['account.move.line']
        lines = Line.search(
            self._base_domain(),
            order='account_id, date, id',
        )
        by_account = {}
        for l in lines:
            acc = l.account_id
            bucket = by_account.setdefault(acc.id, {
                'code': acc.code or '',
                'name': acc.name or '',
                'lines': [],
                'total_debit': 0.0,
                'total_credit': 0.0,
            })
            bucket['lines'].append({
                'date': l.date,
                'move': l.move_id.name,
                'label': l.name or l.move_id.ref or '',
                'partner': l.partner_id.name or '',
                'debit': l.debit,
                'credit': l.credit,
            })
            bucket['total_debit'] += l.debit
            bucket['total_credit'] += l.credit
        # saldo por cuenta + orden
        accounts = []
        for acc_id, b in by_account.items():
            b['saldo'] = b['total_debit'] - b['total_credit']
            running = 0.0
            for ln in b['lines']:
                running += ln['debit'] - ln['credit']
                ln['saldo'] = running
            self._fmt_rows(b['lines'], ['debit', 'credit', 'saldo'])
            b['total_debit_s'] = self._money(b['total_debit'])
            b['total_credit_s'] = self._money(b['total_credit'])
            b['saldo_s'] = self._money(b['saldo'])
            accounts.append(b)
        accounts.sort(key=lambda a: a['code'])
        return {'accounts': accounts}

    # ------------------------------------------------------------------
    #  Datos base compartidos por las plantillas
    # ------------------------------------------------------------------
    def _report_header(self):
        return {
            'company': self.company_id.name,
            'ruc': self.company_id.vat or '',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'target_move': dict(self._fields['target_move'].selection).get(self.target_move),
        }

    def _build_report_data(self, report_type):
        self.ensure_one()
        header = self._report_header()
        if report_type == 'financial_position':
            body = self._compute_financial_position()
        elif report_type == 'income_statement':
            body = self._compute_income_statement()
        elif report_type == 'trial_balance':
            body = self._compute_trial_balance()
        elif report_type == 'general_ledger':
            body = self._compute_general_ledger()
        else:
            raise UserError(_('Tipo de reporte desconocido: %s') % report_type)
        return {
            'wizard_id': self.id,
            'header': header,
            'report_type': report_type,
            **body,
        }

    # ------------------------------------------------------------------
    #  Acciones (botones del asistente)
    # ------------------------------------------------------------------
    def _print(self, xmlid, report_type):
        if self.date_from > self.date_to:
            raise UserError(_('La fecha "Desde" no puede ser posterior a "Hasta".'))
        data = self._build_report_data(report_type)
        return self.env.ref(xmlid).report_action(self, data=data)

    def action_financial_position(self):
        return self._print('pierinelli_reportes.action_report_financial_position',
                            'financial_position')

    def action_income_statement(self):
        return self._print('pierinelli_reportes.action_report_income_statement',
                            'income_statement')

    def action_trial_balance(self):
        return self._print('pierinelli_reportes.action_report_trial_balance',
                            'trial_balance')

    def action_general_ledger(self):
        return self._print('pierinelli_reportes.action_report_general_ledger',
                            'general_ledger')


class ReportFinancialPosition(models.AbstractModel):
    _name = 'report.pierinelli_reportes.report_financial_position_doc'
    _description = 'Datos Balance General'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.financial.report.wizard'].browse(data['wizard_id'])
        # 'o'/'docs' deben ser un recordset (el layout estandar usa o._name,
        # o.id, o.env). Nuestros datos calculados van en 'doc'.
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}


class ReportIncomeStatement(models.AbstractModel):
    _name = 'report.pierinelli_reportes.report_income_statement_doc'
    _description = 'Datos Estado de Resultados'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.financial.report.wizard'].browse(data['wizard_id'])
        # 'o'/'docs' deben ser un recordset (el layout estandar usa o._name,
        # o.id, o.env). Nuestros datos calculados van en 'doc'.
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}


class ReportTrialBalance(models.AbstractModel):
    _name = 'report.pierinelli_reportes.report_trial_balance_doc'
    _description = 'Datos Balance de Comprobacion'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.financial.report.wizard'].browse(data['wizard_id'])
        # 'o'/'docs' deben ser un recordset (el layout estandar usa o._name,
        # o.id, o.env). Nuestros datos calculados van en 'doc'.
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}


class ReportGeneralLedger(models.AbstractModel):
    _name = 'report.pierinelli_reportes.report_general_ledger_doc'
    _description = 'Datos Libro Mayor'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.financial.report.wizard'].browse(data['wizard_id'])
        # 'o'/'docs' deben ser un recordset (el layout estandar usa o._name,
        # o.id, o.env). Nuestros datos calculados van en 'doc'.
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}
