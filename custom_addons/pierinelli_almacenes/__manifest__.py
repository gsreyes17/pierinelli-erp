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

100% Odoo Community. Backend. Marca Pierinelli (negro/dorado).
""",
    'author': 'Pierinelli',
    'website': 'https://pierinelli.com',
    'license': 'LGPL-3',
    'depends': ['stock', 'pierinelli_data'],
    'data': [
        'views/dashboard_action.xml',
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
