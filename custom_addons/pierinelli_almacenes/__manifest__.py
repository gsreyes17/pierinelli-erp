# -*- coding: utf-8 -*-
{
    'name': 'Pierinelli Panorama de Almacenes',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Tablero visual de las sedes: ocupacion, valor, mapa e inventario destacado',
    'description': """
Tablero interactivo 'Panorama de Almacenes' para Pierinelli.
Muestra las 5 sedes con tarjetas (m2 en stock, valor de inventario, nº de
productos, barra de ocupacion), un mapa del Peru con la ubicacion de cada sede
y un ranking de los productos con mayor stock (con foto).

Incluye ademas 7 reportes PDF de almacen con la marca Pierinelli
(Inventario > Reportes > Reportes de Almacen):
- Existencias valorizadas por sede.
- Composicion del inventario por categoria.
- Stock critico (bajo un umbral configurable).
- Antiguedad del inventario (dias en almacen).
- Kardex de movimientos por producto.
- Transferencias entre sedes.
- Rotacion: salidas a clientes y entradas de compras.

100% Odoo Community. Backend. Marca Pierinelli (negro/dorado).
""",
    'author': 'Pierinelli',
    'website': 'https://pierinelli.com',
    'license': 'LGPL-3',
    'depends': ['stock', 'pierinelli_data', 'pierinelli_reportes'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_action.xml',
        'wizard/stock_report_wizard_views.xml',
        'report/stock_report_actions.xml',
        'report/stock_report_docs.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pierinelli_almacenes/static/src/dashboard/*.js',
            'pierinelli_almacenes/static/src/dashboard/*.xml',
            'pierinelli_almacenes/static/src/dashboard/*.scss',
        ],
    },
    'installable': True,
    'application': False,
}
