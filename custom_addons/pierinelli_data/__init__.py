# -*- coding: utf-8 -*-
import base64
from odoo.tools import file_open


def _set_initial_stock(env):
    """Carga inicial: marca en PDF (logo + colores de la compania).

    El stock ya NO se crea aqui: en el modelo V2 cada plancha es un lote con
    codigo interno y medidas, y las genera el seed (seed_pe.py, bloque 7).
    """
    company = env.ref('base.main_company', raise_if_not_found=False)
    if company:
        try:
            with file_open('pierinelli_data/static/img/logo_negro.png', 'rb') as f:
                company.logo = base64.b64encode(f.read())
        except Exception:
            pass
        company.primary_color = '#C9962F'
        company.secondary_color = '#111111'
