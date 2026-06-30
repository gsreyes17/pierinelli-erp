# -*- coding: utf-8 -*-
import base64
from odoo.tools import file_open


def _set_initial_stock(env):
    """Carga inicial: marca en PDF (logo + colores) y stock de muestra."""

    # --- Marca en reportes/PDF: logo negro (visible en blanco) + colores ---
    company = env.ref('base.main_company', raise_if_not_found=False)
    if company:
        try:
            with file_open('pierinelli_data/static/img/logo_negro.png', 'rb') as f:
                company.logo = base64.b64encode(f.read())
        except Exception:
            pass
        company.primary_color = '#C9962F'
        company.secondary_color = '#111111'

    # --- Stock inicial (m2) en el almacen Urban Gallery ---
    warehouse = env.ref('stock.warehouse0', raise_if_not_found=False)
    if not warehouse:
        return
    location = warehouse.lot_stock_id
    Quant = env['stock.quant']
    initial_qty = {
        'CUA-ENIGMA': 120.0,
        'ONX-ORO': 45.0,
        'GRA-MAORI': 200.0,
        'MAR-PORTORO': 60.0,
        'SIN-AMAZONICO': 150.0,
        'CRZ-CALACATTA': 90.0,
    }
    for code, qty in initial_qty.items():
        product = env['product.product'].search(
            [('default_code', '=', code)], limit=1)
        if product:
            Quant._update_available_quantity(product, location, qty)
