from odoo.tests.common import TransactionCase


class TestInventoryAssistant(TransactionCase):
    def test_respuestas_aprobadas_y_limite_del_chat(self):
        assistant = self.env['pierinelli.mcp.inventory.assistant']
        for question in (
            'Que stock vendible hay actualmente',
            'Que reservas vencen hoy o ya vencieron',
            'Que planchas naturales no tienen foto',
            'Cuantas mermas hay este mes',
            'Que planchas estan pendientes de revision',
        ):
            self.assertTrue(assistant.get_chat_answer(question))

        self.assertEqual(
            assistant.get_chat_answer('Como actualizo una factura'),
            'Por ahora solo puedo responder consultas generales de inventario. '
            'Esa clase de consultas aun no estan disponible.',
        )
