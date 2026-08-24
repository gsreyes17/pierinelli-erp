# -*- coding: utf-8 -*-
"""Snapshot por SQL de las ordenes de corte ANTES de que el ORM recalcule los
campos almacenados con la nueva definicion (que, sin secciones todavia,
pondria los totales — incluida la merma congelada de las ordenes ya
ejecutadas — en cero). La post-migracion consume y elimina esta tabla."""


def migrate(cr, version):
    cr.execute("DROP TABLE IF EXISTS pierinelli_oc_legacy_snapshot")
    cr.execute("""
        CREATE TABLE pierinelli_oc_legacy_snapshot AS
        SELECT id, plancha_id, retorno_largo, retorno_alto,
               destino_merma, plancha_retorno_id, m2_merma
          FROM pierinelli_orden_corte
    """)
