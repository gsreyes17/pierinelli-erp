from odoo.tests.common import TransactionCase


class TestTipoCambioSunat(TransactionCase):
    def test_parser_obtiene_ultima_tasa_sunat_de_tabla(self):
        source = b'''<html><body><table>
            <tr><th>Fecha</th><th>Compra</th><th>Venta</th></tr>
            <tr><td>08/08/2026</td><td>3.390</td><td>3.400</td></tr>
            <tr><td>11/08/2026</td><td>3.401</td><td>3.412</td></tr>
        </table></body></html>'''
        fecha, compra, venta = self.env['pierinelli.tipo.cambio']._parse_sunat_html(source)
        self.assertEqual(fecha.isoformat(), '2026-08-11')
        self.assertEqual(compra, 3.401)
        self.assertEqual(venta, 3.412)
