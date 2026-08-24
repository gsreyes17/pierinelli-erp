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

    def test_parser_sunat_acepta_tabla_mensual_con_solo_dia(self):
        source = b'''<html><body><table>
            <tr><th>Dia</th><th>Compra</th><th>Venta</th></tr>
            <tr><td>20</td><td>3.701</td><td>3.711</td></tr>
            <tr><td>21</td><td>3.702</td><td>3.712</td></tr>
        </table></body></html>'''
        fecha, compra, venta = self.env['pierinelli.tipo.cambio']._parse_sunat_html(
            source, 2026, 8)
        self.assertEqual(fecha.isoformat(), '2026-08-21')
        self.assertEqual(compra, 3.702)
        self.assertEqual(venta, 3.712)

    def test_tasa_corporativa_manual_conserva_su_origen(self):
        rate = self.env['pierinelli.tipo.cambio'].create({
            'fecha': '2099-01-01', 'origen': 'corporativa',
            'compra': 3.70, 'venta': 3.75,
        })
        self.assertEqual(rate.origen, 'corporativa')
        self.assertEqual(self.env['pierinelli.tipo.cambio'].tasa_vigente(
            'corporativa', rate.fecha), 3.75)
