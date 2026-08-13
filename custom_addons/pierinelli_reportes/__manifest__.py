# -*- coding: utf-8 -*-
{
    'name': 'Pierinelli Reportes Financieros',
    'version': '19.0.2.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Estados financieros peruanos (Balance General, EE.RR., Mayor, Balance de Comprobacion)',
    'description': """
Reportes financieros completos para Pierinelli sobre Odoo Community.
Community no incluye los estados financieros con formato oficial (eso es
Enterprise); este modulo los construye directamente sobre account.move.line
usando la estructura del Plan Contable General Empresarial (PCGE) peruano.

Incluye 10 reportes:
- Estado de Situacion Financiera (Balance General) por clase PCGE.
- Estado de Resultados (Ganancias y Perdidas) por naturaleza.
- Flujo de Caja (efectivo clase 10: inicial, entradas/salidas, final).
- Indicadores Financieros (liquidez, endeudamiento, ROA/ROE, margenes).
- Libro Diario (asientos del periodo).
- Libro Mayor por cuenta.
- Balance de Comprobacion (sumas y saldos).
- Antiguedad de Cuentas por Cobrar (buckets 30/60/90/+90 dias).
- Antiguedad de Cuentas por Pagar.
- Resumen de IGV (debito vs credito fiscal, estilo PDT 621).
Todos con filtro de fechas y salida PDF con la marca Pierinelli.

Ademas:
- Renombra el menu 'Facturacion' a 'Contabilidad' para el usuario final.
- Tipos de cambio configurables (SUNAT / Corporativa): el vendedor elige la
  tasa en la factura y queda registrado cual se uso.
- Plantillas de asientos contables reutilizables (planilla, depreciacion...).
""",
    'author': 'Pierinelli',
    'website': 'https://pierinelli.com',
    'license': 'LGPL-3',
    'depends': ['account', 'pierinelli_data'],
    'data': [
        'security/ir.model.access.csv',
        'data/multimoneda.xml',
        'data/tipo_cambio_cron.xml',
        'views/contabilidad_extra_views.xml',
        'wizard/financial_report_wizard_views.xml',
        'report/report_actions.xml',
        'report/report_templates.xml',
        'report/report_financial_position.xml',
        'report/report_income_statement.xml',
        'report/report_trial_balance.xml',
        'report/report_general_ledger.xml',
        'report/report_aged.xml',
        'report/report_journal_book.xml',
        'report/report_cash_flow.xml',
        'report/report_tax_summary.xml',
        'report/report_ratios.xml',
        'views/menus.xml',
    ],
    'post_init_hook': '_rename_accounting_menu',
    'installable': True,
    'application': False,
}
