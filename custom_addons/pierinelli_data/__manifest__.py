# -*- coding: utf-8 -*-
{
    'name': 'Pierinelli Datos del Negocio',
    'version': '19.0.1.0.0',
    'category': 'Sales/Inventory',
    'summary': 'Datos base de Pierinelli: compania, almacenes, categorias y productos',
    'description': """
Carga inicial de datos para el negocio de Pierinelli (revestimientos de piedra):
- Datos de la compania (sedes, contacto, moneda PEN).
- Almacenes reales (Urban Gallery, Principal, VES, Trujillo, Arequipa).
- Categorias de producto por tipo de piedra.
- Productos de muestra vendidos por m2 y con control de inventario.
""",
    'author': 'Pierinelli',
    'website': 'https://pierinelli.com',
    'license': 'LGPL-3',
    'depends': ['sale_management', 'stock', 'uom', 'crm'],
    'data': [
        'data/res_company.xml',
        'data/stock_warehouse.xml',
        'data/product_category.xml',
        'data/product_product.xml',
        'data/res_config.xml',
    ],
    'post_init_hook': '_set_initial_stock',
    'installable': True,
    'application': False,
}
