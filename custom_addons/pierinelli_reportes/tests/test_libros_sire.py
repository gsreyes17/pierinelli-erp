import base64
from datetime import date

from odoo.tests.common import TransactionCase


class TestLibrosSire(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Wizard = self.env['pierinelli.libros.sire.wizard']

    def _wizard(self, report_type='ventas_141'):
        return self.Wizard.create({
            'report_type': report_type,
            'date_from': date(2026, 1, 1),
            'date_to': date(2026, 12, 31),
        })

    def test_all_report_sources_prepare_without_error(self):
        for code, _label in self.Wizard._fields['report_type'].selection:
            wizard = self._wizard(code)
            wizard.action_prepare()
            self.assertTrue(wizard.prepared)

    def test_excel_and_txt_have_content_and_warning_name(self):
        wizard = self._wizard()
        wizard.action_prepare()
        wizard.action_export_xlsx()
        self.assertTrue(base64.b64decode(wizard.export_file).startswith(b'PK'))
        self.assertTrue(wizard.export_filename.endswith('.xlsx'))

        wizard.action_export_txt()
        text = base64.b64decode(wizard.export_file).decode('utf-8-sig')
        self.assertIn('|', text)
        self.assertTrue(wizard.export_filename.startswith('LE'))
        self.assertEqual(len(wizard.export_filename.removesuffix('.txt')), 33)

    def test_pdf_template_renders_as_html(self):
        wizard = self._wizard()
        wizard.action_prepare()
        html, kind = self.env['ir.actions.report']._render_qweb_html(
            'pierinelli_reportes.action_report_libros_sire', wizard.ids)
        self.assertEqual(kind, 'html')
        self.assertIn(b'NO PRESENTADO A SUNAT', html)

    def test_classic_accounting_views_have_balanced_debit_credit_columns(self):
        wizard = self._wizard('diario_clasico')
        wizard.action_prepare()
        self.assertEqual(
            round(sum(wizard.line_ids.mapped('debit')), 2),
            round(sum(wizard.line_ids.mapped('credit')), 2),
        )
        for line in wizard.line_ids.filtered('tax_amount'):
            self.assertTrue(line.tax_info)
            self.assertTrue(line.tax_account)
            self.assertAlmostEqual(line.tax_amount, abs(line.debit - line.credit), places=2)
        wizard.action_export_xlsx()
        self.assertTrue(base64.b64decode(wizard.export_file).startswith(b'PK'))

    def test_classic_accounting_reports_show_positive_debit_credit_balances(self):
        """Los saldos se exponen en sus columnas naturales, nunca con signo."""
        ledger = self._wizard('mayor_clasico')
        ledger.action_prepare()
        for line in ledger.line_ids:
            self.assertGreaterEqual(line.balance_debit, 0.0)
            self.assertGreaterEqual(line.balance_credit, 0.0)
            self.assertFalse(line.balance_debit and line.balance_credit)

        trial = self._wizard('balance_comprobacion')
        trial.action_prepare()
        for line in trial.line_ids:
            self.assertGreaterEqual(line.opening_debit, 0.0)
            self.assertGreaterEqual(line.opening_credit, 0.0)
            self.assertGreaterEqual(line.closing_debit, 0.0)
            self.assertGreaterEqual(line.closing_credit, 0.0)
            self.assertFalse(line.opening_debit and line.opening_credit)
            self.assertFalse(line.closing_debit and line.closing_credit)
            signed_opening = line.opening_debit - line.opening_credit
            signed_closing = line.closing_debit - line.closing_credit
            self.assertAlmostEqual(
                signed_closing, signed_opening + line.debit - line.credit, places=2)

    def test_format_help_opens_a_modal_record(self):
        wizard = self._wizard()
        action = wizard.action_show_format_help()
        self.assertEqual(action['res_model'], 'pierinelli.libros.sire.help')
        self.assertEqual(action['target'], 'new')
