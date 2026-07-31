# -*- coding: utf-8 -*-
from . import models
from . import wizard


def _rename_accounting_menu(env):
    """Renombra la app 'Facturacion' -> 'Contabilidad' en TODOS los idiomas.

    El nombre del menu es traducible; como la BD carga es_419, la traduccion
    'Facturacion' se impone sobre el valor base. Aqui forzamos el nombre en el
    valor base y en cada idioma activo para que el usuario final vea
    'Contabilidad'.
    """
    menu = env.ref('account.menu_finance', raise_if_not_found=False)
    if not menu:
        return
    langs = [code for code, _name in env['res.lang'].get_installed()]
    for lang in (langs or [env.context.get('lang') or 'en_US']):
        menu.with_context(lang=lang).write({'name': 'Contabilidad'})
