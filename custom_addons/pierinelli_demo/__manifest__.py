# -*- coding: utf-8 -*-
{
    'name': 'Pierinelli Demo',
    'version': '19.0.1.0.0',
    'category': 'Sales/Inventory',
    'summary': 'Datos de demostracion: clientes, ventas entregadas y oportunidades CRM',
    'description': """
Carga una demostracion funcional completa y reproducible (vía post_init_hook):
- Clientes / estudios de arquitectura.
- Pedidos de venta confirmados y entregados (descuento de stock real).
- Oportunidades en el embudo CRM.
- Idioma espanol por defecto.

Pensado para que un despliegue desde cero (Docker / Render) reproduzca la demo
sin necesidad de restaurar respaldos.
""",
    'author': 'Pierinelli',
    'website': 'https://pierinelli.com',
    'license': 'LGPL-3',
    'depends': ['pierinelli_data'],
    'data': [],
    'post_init_hook': '_load_demo',
    'installable': True,
    'application': False,
}
