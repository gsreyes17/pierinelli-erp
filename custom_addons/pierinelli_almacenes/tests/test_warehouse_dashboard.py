from odoo.tests.common import TransactionCase


class TestWarehouseDashboard(TransactionCase):
    def test_payload_del_tablero(self):
        data = self.env['pierinelli.warehouse.dashboard'].get_dashboard_data()
        self.assertEqual(set(data), {'sedes', 'productos', 'totales', 'moneda'})
        for sede in data['sedes']:
            self.assertTrue({'id', 'name', 'ocupacion'} <= set(sede))
        for product in data['productos']:
            self.assertTrue({'id', 'name', 'image'} <= set(product))
