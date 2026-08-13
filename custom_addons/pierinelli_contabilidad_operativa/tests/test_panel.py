import base64
import io

import xlsxwriter

from odoo.tests.common import TransactionCase


class TestPanelContable(TransactionCase):
    def test_indicadores_y_acciones_disponibles(self):
        data = self.env['pierinelli.panel.contable'].get_data()
        self.assertEqual(set(data), {
            'borradores', 'por_cobrar', 'por_pagar', 'cajas_abiertas',
            'tributos_pendientes', 'presupuestos_abiertos', 'arqueos_pendientes',
        })
        self.assertTrue(all(isinstance(value, int) for value in data.values()))

        for xmlid in (
            'account.action_move_journal_line',
            'account.action_move_out_invoice_type',
            'account.action_move_in_invoice_type',
            'pierinelli_contabilidad_operativa.action_caja_chica',
            'pierinelli_contabilidad_operativa.action_control_tributario',
            'pierinelli_contabilidad_operativa.action_arqueo_cobranza',
            'pierinelli_contabilidad_operativa.action_cierre_contable',
            'pierinelli_contabilidad_operativa.action_descargar_plantilla_asientos',
            'pierinelli_contabilidad_operativa.action_importar_asientos',
            'pierinelli_contabilidad_operativa.action_presupuesto',
            'pierinelli_reportes.action_plantilla_asiento',
        ):
            self.assertTrue(self.env.ref(xmlid, raise_if_not_found=False), xmlid)

    def test_cierre_contable_aplica_bloqueo_estandar_y_se_puede_revertir(self):
        company = self.env.company
        previous = company.fiscalyear_lock_date
        cierre = self.env['pierinelli.cierre.contable'].create({
            'name': 'Cierre de prueba',
            'company_id': company.id,
            'fecha_bloqueo': '2026-07-31',
            'tipo': 'fiscal',
        })
        cierre.action_aplicar()
        self.assertEqual(company.fiscalyear_lock_date.isoformat(), '2026-07-31')
        self.assertEqual(cierre.state, 'aplicado')
        cierre.action_revertir()
        self.assertEqual(company.fiscalyear_lock_date, previous)
        self.assertEqual(cierre.state, 'revertido')

    def test_arqueo_de_cobranzas_requiere_confirmacion(self):
        account = self.env['account.account'].search([
            ('company_ids', 'in', self.env.company.id)], limit=1)
        journal = self.env['account.journal'].create({
            'name': 'Caja pruebas arqueo',
            'code': 'TARQ',
            'type': 'cash',
            'company_id': self.env.company.id,
            'default_account_id': account.id,
        })
        arqueo = self.env['pierinelli.arqueo.cobranza'].create({
            'name': 'Arqueo pruebas', 'journal_id': journal.id,
            'fecha': '2026-08-01',
        })
        self.assertEqual(arqueo.importe_esperado, 0.0)
        with self.assertRaises(Exception):
            arqueo.action_cerrar()
        arqueo.write({'efectivo_contado': 0.0, 'arqueo_confirmado': True})
        arqueo.action_cerrar()
        self.assertEqual(arqueo.state, 'cerrado')

    def test_importador_de_asientos_valida_y_crea_borrador(self):
        journal = self.env['account.journal'].search([
            ('type', '=', 'general'), ('company_id', '=', self.env.company.id)],
            limit=1)
        accounts = self.env['account.account'].search([
            ('company_ids', 'in', self.env.company.id)], limit=2)
        self.assertTrue(journal)
        self.assertEqual(len(accounts), 2)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Asientos')
        headers = ['referencia', 'fecha', 'diario_codigo', 'cuenta_codigo',
                   'glosa', 'debe', 'haber', 'tipo_operacion']
        for column, header in enumerate(headers):
            sheet.write(0, column, header)
        sheet.write_row(1, 0, ['TEST-IMPORT-001', '12/08/2026', journal.code,
                               accounts[0].code, 'Debe de prueba', 100, 0,
                               'ajuste'])
        sheet.write_row(2, 0, ['TEST-IMPORT-001', '12/08/2026', journal.code,
                               accounts[1].code, 'Haber de prueba', 0, 100,
                               'ajuste'])
        workbook.close()
        wizard = self.env['pierinelli.importar.asientos'].create({
            'archivo': base64.b64encode(output.getvalue()),
            'archivo_nombre': 'asientos.xlsx',
        })
        action = wizard.action_importar()
        move = self.env['account.move'].search([
            ('ref', '=', 'TEST-IMPORT-001')], limit=1)
        self.assertEqual(action['res_model'], 'account.move')
        self.assertTrue(move)
        self.assertEqual(move.state, 'draft')
        self.assertEqual(sum(move.line_ids.mapped('debit')),
                         sum(move.line_ids.mapped('credit')))
