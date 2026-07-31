# -*- coding: utf-8 -*-
from . import models
from . import wizard


def _rename_accounting_menu(env):
    """La app 'Facturacion' se presenta como 'Contabilidad' (como Enterprise).

    - Renombra el menu raiz en TODOS los idiomas (el nombre es traducible y
      la traduccion es_419 se impone al valor base).
    - Al entrar a la app se abre el TABLERO de diarios (como el Accounting
      de Enterprise) titulado 'Contabilidad', en vez de caer en la lista
      'Facturas'.
    - El submenu de configuracion 'Facturacion' tambien pasa a 'Contabilidad'.
    """
    menu = env.ref('account.menu_finance', raise_if_not_found=False)
    if not menu:
        return
    langs = [code for code, _name in env['res.lang'].get_installed()]
    langs = langs or [env.context.get('lang') or 'en_US']
    for lang in langs:
        menu.with_context(lang=lang).write({'name': 'Contabilidad'})

    # Tablero como pagina de inicio de la app, titulado 'Contabilidad'
    dashboard = env.ref('account.open_account_journal_dashboard_kanban',
                        raise_if_not_found=False)
    if dashboard:
        for lang in langs:
            dashboard.with_context(lang=lang).write({'name': 'Contabilidad'})
        menu.write({'action': 'ir.actions.act_window,%d' % dashboard.id})

    # Submenu Configuracion > 'Facturacion' -> 'Contabilidad'
    for sub in env['ir.ui.menu'].search([('id', 'child_of', menu.id)]):
        for lang in langs:
            s = sub.with_context(lang=lang)
            if s.name == 'Facturacion' or s.name == 'Facturación':
                s.write({'name': 'Contabilidad'})
