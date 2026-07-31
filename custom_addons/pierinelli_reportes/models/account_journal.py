# -*- coding: utf-8 -*-
"""
Bloqueo amable del boton "Subir factura" para archivos que Community no
puede leer (Plan V2 §9.2).

La lectura automatica de facturas en PDF (OCR) es de Odoo Enterprise. Lo que
SI funciona en Community es importar el XML de la factura electronica
(UBL/SUNAT). Aqui, en lugar de crear una factura vacia y un mensaje confuso,
se explica claramente que hacer.
"""
from odoo import models, _
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def create_document_from_attachment(self, attachment_ids):
        adjuntos = self.env['ir.attachment'].browse(attachment_ids or [])
        no_xml = adjuntos.filtered(
            lambda a: 'xml' not in (a.mimetype or '')
            and not (a.name or '').lower().endswith('.xml'))
        if no_xml:
            raise UserError(_(
                'Lectura automatica no disponible en esta version.\n\n'
                'El reconocimiento de facturas en PDF/imagen (OCR) es una '
                'funcion de Odoo Enterprise. En esta version puedes:\n\n'
                '  1. Subir el XML de la factura electronica (el proveedor '
                'esta obligado a entregarlo junto al PDF): ese SI se importa '
                'automaticamente.\n'
                '  2. Crear la factura manualmente y adjuntarle el PDF como '
                'referencia.\n\n'
                'Archivo(s) no procesable(s): %s')
                % ', '.join(no_xml.mapped('name')))
        return super().create_document_from_attachment(attachment_ids)
