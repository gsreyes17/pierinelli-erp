# -*- coding: utf-8 -*-
"""Ordenes de corte multi-plancha: convierte cada orden previa (una plancha
en la cabecera) en una orden con UNA seccion equivalente, re-vincula sus
lineas y restaura la merma congelada desde el snapshot de la pre-migracion.
Idempotente: solo toca ordenes sin secciones."""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("""SELECT id, plancha_id, retorno_largo, retorno_alto,
                         destino_merma, plancha_retorno_id, m2_merma
                    FROM pierinelli_oc_legacy_snapshot""")
    viejo = {fila[0]: fila for fila in cr.fetchall()}

    Orden = env['pierinelli.orden.corte']
    Seccion = env['pierinelli.orden.corte.plancha']
    pendientes = Orden.search([('plancha_ids', '=', False),
                               ('plancha_id', '!=', False)])
    for orden in pendientes:
        (_oid, plancha_id, ret_l, ret_a, destino, retorno_id,
         m2_merma) = viejo.get(orden.id, (orden.id, orden.plancha_id.id,
                                          orden.retorno_largo,
                                          orden.retorno_alto,
                                          orden.destino_merma, False, 0.0))
        seccion = Seccion.create({
            'orden_id': orden.id,
            'plancha_id': plancha_id,
            'retorno_largo': ret_l or 0.0,
            'retorno_alto': ret_a or 0.0,
            'destino_merma': destino or 'negocio',
            'plancha_retorno_id': retorno_id or False,
        })
        orden.linea_ids.write({'seccion_id': seccion.id})
        if orden.state == 'hecho':
            # La merma quedo congelada al ejecutar; la seccion la hereda tal
            # cual (su compute no recalcula en estado 'hecho').
            seccion.m2_merma = m2_merma or 0.0
    cr.execute("DROP TABLE IF EXISTS pierinelli_oc_legacy_snapshot")
