{
    'name': 'Pierinelli Contabilidad Operativa',
    'version': '19.0.2.1.0',
    'summary': 'Control contable, caja chica, tesoreria y cumplimiento operativo',
    'author': 'Pierinelli',
    'depends': ['account', 'analytic', 'pierinelli_reportes'],
    'data': [
        'security/ir.model.access.csv',
        'data/admin_access.xml',
        'data/tipos_comprobante.xml',
        'views/contabilidad_views.xml',
        'views/accounting_extensions_views.xml',
        'views/analytic_account_views.xml',
        'views/presupuesto_views.xml',
        'views/control_operativo_views.xml',
        'views/importar_asientos_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pierinelli_contabilidad_operativa/static/src/panel/*.js',
            'pierinelli_contabilidad_operativa/static/src/panel/*.xml',
            'pierinelli_contabilidad_operativa/static/src/panel/*.scss',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
