# -*- coding: utf-8 -*-
{
    'name': 'Pierinelli Reportes Financieros',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Estados financieros peruanos (Balance General, EE.RR., Mayor, Balance de Comprobacion)',
    'description': """
Reportes financieros completos para Pierinelli sobre Odoo Community.
Community no incluye los estados financieros con formato oficial (eso es
Enterprise); este modulo los construye directamente sobre account.move.line
usando la estructura del Plan Contable General Empresarial (PCGE) peruano.

Incluye:
- Estado de Situacion Financiera (Balance General) por clase PCGE.
- Estado de Resultados (Ganancias y Perdidas) por naturaleza.
- Balance de Comprobacion (sumas y saldos).
- Libro Mayor por cuenta.
- Indicadores en el Estado de Resultados (ingresos, gastos, utilidad, margen).
Todos con filtro de fechas y salida PDF con la marca Pierinelli.

Ademas renombra el menu 'Facturacion' a 'Contabilidad' para el usuario final.
""",
    'author': 'Pierinelli',
    'website': 'https://pierinelli.com',
    'license': 'LGPL-3',
    'depends': ['account', 'pierinelli_data'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/financial_report_wizard_views.xml',
        'report/report_actions.xml',
        'report/report_templates.xml',
        'report/report_financial_position.xml',
        'report/report_income_statement.xml',
        'report/report_trial_balance.xml',
        'report/report_general_ledger.xml',
        'views/menus.xml',
    ],
    'post_init_hook': '_rename_accounting_menu',
    'installable': True,
    'application': False,
}
