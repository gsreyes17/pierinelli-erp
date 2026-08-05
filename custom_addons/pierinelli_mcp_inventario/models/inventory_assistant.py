# -*- coding: utf-8 -*-
"""Consultas de solo lectura para el chat flotante de inventario."""
import re
import unicodedata

from odoo import api, fields, models, _


def _normalizar_mensaje(texto):
    """Compara mensajes sin depender de mayusculas, tildes o signos."""
    texto = unicodedata.normalize('NFD', texto or '')
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^\w\s]', ' ', texto.casefold())
    return ' '.join(texto.split())


DISPARADORES_CHAT = {
    _normalizar_mensaje('Que stock vendible hay actualmente'): 'stock',
    _normalizar_mensaje('Que reservas vencen hoy o ya vencieron'): 'reservas',
    _normalizar_mensaje('Que planchas naturales no tienen foto'): 'naturales_sin_foto',
    _normalizar_mensaje('Cuantas mermas hay este mes'): 'mermas_mes',
    _normalizar_mensaje('Que planchas estan pendientes de revision'): 'pendientes',
}


class InventoryAssistant(models.TransientModel):
    _name = 'pierinelli.mcp.inventory.assistant'
    _description = 'Asistente de Inventario'

    pregunta = fields.Selection([
        ('stock', 'Stock vendible actual'),
        ('reservas', 'Reservas vencidas'),
        ('naturales_sin_foto', 'Naturales sin foto'),
        ('mermas_mes', 'Mermas del mes'),
        ('pendientes', 'Planchas pendientes de revision'),
    ], string='Consulta', required=True, default='stock')
    respuesta = fields.Text('Respuesta', readonly=True)

    @api.model
    def get_answer(self, pregunta):
        """Ejecuta una consulta predefinida; nunca cambia inventario."""
        wizard = self.create({'pregunta': pregunta})
        wizard.action_consultar()
        return wizard.respuesta

    @api.model
    def get_chat_answer(self, mensaje):
        """Responde solo los cinco dialogos aprobados para esta primera fase."""
        pregunta = DISPARADORES_CHAT.get(_normalizar_mensaje(mensaje))
        if not pregunta:
            return (_('Por ahora solo puedo responder consultas generales de '
                      'inventario. Esa consulta aun no esta habilitada. '
                      'Revisa las frases disponibles en la guia del asistente.'))
        return self.get_answer(pregunta)

    def action_consultar(self):
        self.ensure_one()
        Lot = self.env['stock.lot']
        if self.pregunta == 'stock':
            lots = Lot.search([
                ('m2_disponible', '>', 0),
                ('aptitud_comercial', 'in', ('vendible', 'liquidacion')),
            ])
            self.respuesta = _(
                'Stock comercial disponible: %(m2).2f m2 en %(planchas)d '
                'planchas, correspondientes a %(materiales)d materiales.',
                m2=sum(lots.mapped('m2_disponible')), planchas=len(lots),
                materiales=len(lots.mapped('product_id')))
        elif self.pregunta == 'reservas':
            hoy = fields.Date.context_today(self)
            lots = Lot.search([
                ('cliente_reserva_id', '!=', False),
                ('reserva_fin', '<=', hoy),
                ('m2_disponible', '>', 0),
            ], order='reserva_fin, name')
            detalle = ', '.join('%s (%s)' % (lot.name, lot.reserva_fin)
                                for lot in lots[:10])
            self.respuesta = (_('No hay reservas vencidas al %(fecha)s.') %
                              {'fecha': hoy} if not lots else
                              _('Hay %(cantidad)d reservas por liberar: %(detalle)s.')
                              % {'cantidad': len(lots), 'detalle': detalle})
        elif self.pregunta == 'naturales_sin_foto':
            lots = Lot.search([
                ('tipo_material', '=', 'natural'),
                ('image_1920', '=', False),
                ('m2_disponible', '>', 0),
            ], order='name')
            detalle = ', '.join(lots[:10].mapped('name'))
            self.respuesta = (_('Todas las planchas naturales con stock tienen foto individual.')
                              if not lots else
                              _('%(cantidad)d planchas naturales requieren foto: %(detalle)s.')
                              % {'cantidad': len(lots), 'detalle': detalle})
        elif self.pregunta == 'mermas_mes':
            hoy = fields.Date.context_today(self)
            mermas = self.env['pierinelli.merma'].search([
                ('fecha', '>=', hoy.replace(day=1)),
            ])
            self.respuesta = _(
                'En el mes actual se registraron %(cantidad)d mermas por un '
                'total de %(m2).2f m2.', cantidad=len(mermas),
                m2=sum(mermas.mapped('m2')))
        else:
            lots = Lot.search([
                ('aptitud_comercial', '=', 'pendiente'),
                ('m2_disponible', '>', 0),
            ], order='name')
            detalle = ', '.join(lots[:10].mapped('name'))
            self.respuesta = (_('No hay planchas pendientes de revision con stock.')
                              if not lots else
                              _('%(cantidad)d planchas requieren revision: %(detalle)s.')
                              % {'cantidad': len(lots), 'detalle': detalle})
        return True
