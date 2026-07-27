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
    #  Antiguedad de saldos (CxC / CxP) - partidas abiertas por tercero,
    #  clasificadas por dias de vencimiento respecto a la fecha "Hasta".
    # ------------------------------------------------------------------
    def _compute_aged(self, account_type):
        Line = self.env['account.move.line']
        domain = [
            ('company_id', '=', self.company_id.id),
            ('account_id.account_type', '=', account_type),
            ('date', '<=', self.date_to),
            ('amount_residual', '!=', 0),
        ]
        if self.target_move == 'posted':
            domain.append(('parent_state', '=', 'posted'))
        else:
            domain.append(('parent_state', 'in', ('posted', 'draft')))

        # CxC: residual positivo = nos deben. CxP: residual negativo = debemos.
        sign = 1.0 if account_type == 'asset_receivable' else -1.0
        buckets = ['no_vencido', 'b30', 'b60', 'b90', 'mas90']
        partners = {}
        for l in Line.search(domain):
            due = l.date_maturity or l.date
            dias = (self.date_to - due).days
            if dias <= 0:
                key = 'no_vencido'
            elif dias <= 30:
                key = 'b30'
            elif dias <= 60:
                key = 'b60'
            elif dias <= 90:
                key = 'b90'
            else:
                key = 'mas90'
            pid = l.partner_id.id or 0
            row = partners.setdefault(pid, {
                'partner': l.partner_id.name or '(Sin tercero)',
                'vat': l.partner_id.vat or '',
                'no_vencido': 0.0, 'b30': 0.0, 'b60': 0.0,
                'b90': 0.0, 'mas90': 0.0, 'total': 0.0,
            })
            amt = sign * l.amount_residual
            row[key] += amt
            row['total'] += amt

        rows = sorted(partners.values(), key=lambda r: -abs(r['total']))
        keys = buckets + ['total']
        totals = {b: sum(r[b] for r in rows) for b in keys}
        self._fmt_rows(rows, keys)
        totals.update({b + '_s': self._money(totals[b]) for b in keys})
        es_cxc = account_type == 'asset_receivable'
        return {
            'rows': rows,
            'totals': totals,
            'titulo': ('Antiguedad de Cuentas por Cobrar' if es_cxc
                       else 'Antiguedad de Cuentas por Pagar'),
            'tercero_lbl': 'Cliente' if es_cxc else 'Proveedor',
        }

    # ------------------------------------------------------------------
    #  Libro Diario - asientos del periodo con sus apuntes
    # ------------------------------------------------------------------
    def _compute_journal_book(self):
        Move = self.env['account.move']
        domain = [
            ('company_id', '=', self.company_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        if self.target_move == 'posted':
            domain.append(('state', '=', 'posted'))
        else:
            domain.append(('state', 'in', ('posted', 'draft')))
        moves = Move.search(domain, order='date, name')
        entries = []
        tot_d = tot_c = 0.0
        for m in moves:
            lines = []
            for l in m.line_ids:
                if l.display_type in ('line_section', 'line_note'):
                    continue
                lines.append({
                    'account': '%s %s' % (l.account_id.code or '', l.account_id.name or ''),
                    'label': l.name or '',
                    'partner': l.partner_id.name or '',
                    'debit_s': self._money(l.debit),
                    'credit_s': self._money(l.credit),
                    'debit': l.debit,
                    'credit': l.credit,
                })
            d = sum(x['debit'] for x in lines)
            c = sum(x['credit'] for x in lines)
            tot_d += d
            tot_c += c
            entries.append({
                'name': m.name,
                'date': m.date,
                'journal': m.journal_id.name,
                'ref': m.ref or '',
                'state': 'Publicado' if m.state == 'posted' else 'Borrador',
                'lines': lines,
                'debit_s': self._money(d),
                'credit_s': self._money(c),
            })
        return {
            'entries': entries,
            'count': len(entries),
            'total_debit_s': self._money(tot_d),
            'total_credit_s': self._money(tot_c),
        }

    # ------------------------------------------------------------------
    #  Flujo de Caja - cuentas de efectivo (clase 10 PCGE): saldo inicial,
    #  entradas/salidas del periodo por diario y saldo final.
    # ------------------------------------------------------------------
    def _compute_cash_flow(self):
        Line = self.env['account.move.line']
        cash_accounts = self.env['account.account'].search([('code', '=like', '10%')])
        state_dom = ([('parent_state', '=', 'posted')] if self.target_move == 'posted'
                     else [('parent_state', 'in', ('posted', 'draft'))])
        base = [('company_id', '=', self.company_id.id),
                ('account_id', 'in', cash_accounts.ids)] + state_dom

        prev = Line.read_group(base + [('date', '<', self.date_from)], ['balance:sum'], [])
        saldo_inicial = (prev[0].get('balance') or 0.0) if prev else 0.0

        period = base + [('date', '>=', self.date_from), ('date', '<=', self.date_to)]
        groups = Line.read_group(period, ['debit:sum', 'credit:sum'], ['journal_id'])
        rows = []
        tot_in = tot_out = 0.0
        for g in groups:
            jname = g['journal_id'][1] if g.get('journal_id') else '(Sin diario)'
            d = g.get('debit') or 0.0
            c = g.get('credit') or 0.0
            rows.append({
                'journal': jname,
                'entradas': d, 'salidas': c, 'neto': d - c,
                'entradas_s': self._money(d),
                'salidas_s': self._money(c),
                'neto_s': self._money(d - c),
            })
            tot_in += d
            tot_out += c
        rows.sort(key=lambda r: -(r['entradas'] + r['salidas']))
        saldo_final = saldo_inicial + tot_in - tot_out
        return {
            'rows': rows,
            'saldo_inicial': saldo_inicial,
            'saldo_inicial_s': self._money(saldo_inicial),
            'total_entradas': tot_in,
            'total_entradas_s': self._money(tot_in),
            'total_salidas': tot_out,
            'total_salidas_s': self._money(tot_out),
            'flujo_neto': tot_in - tot_out,
            'flujo_neto_s': self._money(tot_in - tot_out),
            'saldo_final': saldo_final,
            'saldo_final_s': self._money(saldo_final),
        }

    # ------------------------------------------------------------------
    #  Resumen de IGV - debito fiscal (ventas) vs credito fiscal (compras)
    #  a partir de los apuntes de impuesto del periodo. Estilo PDT 621.
    # ------------------------------------------------------------------
    def _compute_tax_summary(self):
        Line = self.env['account.move.line']
        domain = self._base_domain() + [('tax_line_id', '!=', False)]
        taxes = {}
        for l in Line.search(domain):
            t = l.tax_line_id
            entry = taxes.setdefault(t.id, {
                'name': t.name, 'rate': t.amount,
                'use': t.type_tax_use, 'amount': 0.0,
            })
            # IGV ventas: apunte al haber (balance negativo) -> monto positivo.
            # IGV compras: apunte al debe (balance positivo).
            entry['amount'] += -l.balance if t.type_tax_use == 'sale' else l.balance

        ventas = [v for v in taxes.values() if v['use'] == 'sale']
        compras = [v for v in taxes.values() if v['use'] == 'purchase']
        for grp in (ventas, compras):
            for v in grp:
                v['base'] = v['amount'] / (v['rate'] / 100.0) if v['rate'] else 0.0
                v['base_s'] = self._money(v['base'])
                v['amount_s'] = self._money(v['amount'])
        igv_ventas = sum(v['amount'] for v in ventas)
        igv_compras = sum(v['amount'] for v in compras)
        saldo = igv_ventas - igv_compras
        return {
            'ventas': ventas,
            'compras': compras,
            'igv_ventas': igv_ventas,
            'igv_ventas_s': self._money(igv_ventas),
            'igv_compras': igv_compras,
            'igv_compras_s': self._money(igv_compras),
            'saldo': saldo,
            'saldo_s': self._money(abs(saldo)),
            'a_favor': saldo < 0,
        }

    # ------------------------------------------------------------------
    #  Indicadores financieros - ratios de gestion con interpretacion
    # ------------------------------------------------------------------
    def _compute_ratios(self):
        fp = self._compute_financial_position()
        inc = self._compute_income_statement()

        act_corriente = sum(a['monto'] for a in fp['activo'] if a['code'][:1] in ('1', '2'))
        existencias = sum(a['monto'] for a in fp['activo'] if a['code'][:1] == '2')
        total_activo = fp['total_activo']
        total_pasivo = fp['total_pasivo']
        patrimonio = fp['total_patrimonio']
        ingresos = inc['total_ingresos']
        utilidad = inc['utilidad_neta']
        costo_ventas = sum(g['monto'] for g in inc['gastos']
                           if g['code'].startswith('69')) or inc['total_gastos']

        def div(num, den):
            # None = no calculable (denominador cero); se muestra "n.d."
            return (num / den) if den else None

        def pct(num, den):
            r = div(num, den)
            return r * 100.0 if r is not None else None

        items = [
            {'nombre': 'Liquidez corriente', 'unidad': 'x',
             'formula': 'Activo corriente / Pasivo',
             'valor': div(act_corriente, total_pasivo),
             'lectura': 'Por cada S/ 1 de deuda, hay S/ %.2f en activos de corto plazo.'},
            {'nombre': 'Prueba acida', 'unidad': 'x',
             'formula': '(Activo corriente - Existencias) / Pasivo',
             'valor': div(act_corriente - existencias, total_pasivo),
             'lectura': 'Sin contar el inventario, se cubre %.2f veces la deuda.'},
            {'nombre': 'Endeudamiento', 'unidad': '%',
             'formula': 'Pasivo / Activo',
             'valor': pct(total_pasivo, total_activo),
             'lectura': 'El %.1f%% de los activos esta financiado con deuda.'},
            {'nombre': 'Solvencia patrimonial', 'unidad': '%',
             'formula': 'Patrimonio / Activo',
             'valor': pct(patrimonio, total_activo),
             'lectura': 'El %.1f%% de los activos es capital propio.'},
            {'nombre': 'Margen neto', 'unidad': '%',
             'formula': 'Utilidad neta / Ingresos',
             'valor': pct(utilidad, ingresos),
             'lectura': 'De cada S/ 100 vendidos quedan S/ %.1f de utilidad.'},
            {'nombre': 'ROA (rentab. de activos)', 'unidad': '%',
             'formula': 'Utilidad neta / Activo',
             'valor': pct(utilidad, total_activo),
             'lectura': 'Cada S/ 100 invertidos en activos generan S/ %.1f.'},
            {'nombre': 'ROE (rentab. patrimonial)', 'unidad': '%',
             'formula': 'Utilidad neta / Patrimonio',
             'valor': pct(utilidad, patrimonio),
             'lectura': 'Cada S/ 100 de capital propio generan S/ %.1f.'},
            {'nombre': 'Rotacion de inventario', 'unidad': 'x',
             'formula': 'Costo de ventas / Existencias',
             'valor': div(costo_ventas, existencias),
             'lectura': 'El inventario rota %.2f veces en el periodo.'},
        ]
        for it in items:
            if it['valor'] is None:
                it['valor_s'] = 'n.d.'
                it['lectura'] = 'No calculable con los datos del periodo.'
            elif it['unidad'] == '%':
                it['valor_s'] = '{:,.1f}%'.format(it['valor'])
                it['lectura'] = it['lectura'] % it['valor']
            else:
                it['valor_s'] = '{:,.2f}'.format(it['valor'])
                it['lectura'] = it['lectura'] % it['valor']

        return {
            'items': items,
            'resumen': {
                'total_activo_s': self._money(total_activo),
                'total_pasivo_s': self._money(total_pasivo),
                'patrimonio_s': self._money(patrimonio),
                'ingresos_s': self._money(ingresos),
                'utilidad_s': self._money(utilidad),
            },
        }

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
        elif report_type == 'aged_receivable':
            body = self._compute_aged('asset_receivable')
        elif report_type == 'aged_payable':
            body = self._compute_aged('liability_payable')
        elif report_type == 'journal_book':
            body = self._compute_journal_book()
        elif report_type == 'cash_flow':
            body = self._compute_cash_flow()
        elif report_type == 'tax_summary':
            body = self._compute_tax_summary()
        elif report_type == 'ratios':
            body = self._compute_ratios()
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

    def action_aged_receivable(self):
        return self._print('pierinelli_reportes.action_report_aged',
                            'aged_receivable')

    def action_aged_payable(self):
        return self._print('pierinelli_reportes.action_report_aged',
                            'aged_payable')

    def action_journal_book(self):
        return self._print('pierinelli_reportes.action_report_journal_book',
                            'journal_book')

    def action_cash_flow(self):
        return self._print('pierinelli_reportes.action_report_cash_flow',
                            'cash_flow')

    def action_tax_summary(self):
        return self._print('pierinelli_reportes.action_report_tax_summary',
                            'tax_summary')

    def action_ratios(self):
        return self._print('pierinelli_reportes.action_report_ratios',
                            'ratios')


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


class ReportAged(models.AbstractModel):
    _name = 'report.pierinelli_reportes.report_aged_doc'
    _description = 'Datos Antiguedad de Saldos'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.financial.report.wizard'].browse(data['wizard_id'])
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}


class ReportJournalBook(models.AbstractModel):
    _name = 'report.pierinelli_reportes.report_journal_book_doc'
    _description = 'Datos Libro Diario'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.financial.report.wizard'].browse(data['wizard_id'])
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}


class ReportCashFlow(models.AbstractModel):
    _name = 'report.pierinelli_reportes.report_cash_flow_doc'
    _description = 'Datos Flujo de Caja'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.financial.report.wizard'].browse(data['wizard_id'])
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}


class ReportTaxSummary(models.AbstractModel):
    _name = 'report.pierinelli_reportes.report_tax_summary_doc'
    _description = 'Datos Resumen de IGV'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.financial.report.wizard'].browse(data['wizard_id'])
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}


class ReportRatios(models.AbstractModel):
    _name = 'report.pierinelli_reportes.report_ratios_doc'
    _description = 'Datos Indicadores Financieros'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.financial.report.wizard'].browse(data['wizard_id'])
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}
