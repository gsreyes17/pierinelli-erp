# -*- coding: utf-8 -*-
{
    'name': 'Pierinelli Planchas',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Cada plancha es un lote: codigo interno, medidas, foto, condicion y reserva',
    'description': """
Modelo de inventario por plancha para Pierinelli (Plan Inventario V2).

Cada plancha fisica es un lote (stock.lot) de su producto:
- Codigo interno automatico: iniciales del producto + mes/anio + correlativo
  (ej. Cuarcita Iron Green -> CIG1025.01). Los retornos de corte extienden el
  codigo de la plancha madre (CIG1025.01.01).
- Ficha completa: largo, alto, espesor, m2 neto/bruto, ubicacion referencial,
  ref. de importacion, observaciones y foto (obligatoria solo en naturales).
- Condicion: Estandar / Oferta / Liquidacion / Hueso (esta ultima la marca el
  sistema solo cuando la plancha supera 1 anio en almacen).
- Estado: Disponible / Reservada / Vendida, calculado del stock y la reserva.
- Reserva comercial con vencimiento a 7 dias y liberacion automatica.
- Alta masiva: "20 planchas de 3.40 x 1.65" genera .01 ... .20 de un golpe.
- Vista de Operaciones (tabla completa) y Vista Comercial (sin costos).

100% Odoo Community.
""",
    'author': 'Pierinelli',
    'website': 'https://pierinelli.com',
    'license': 'LGPL-3',
    'depends': ['stock', 'sale_management', 'pierinelli_data',
                'pierinelli_reportes'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/orden_corte_data.xml',
        'views/product_views.xml',
        'views/stock_lot_views.xml',
        'views/sale_order_views.xml',
        'views/alta_planchas_views.xml',
        'views/orden_corte_views.xml',
        'views/stock_quant_views.xml',
        'report/orden_corte_report.xml',
    ],
    'installable': True,
    'application': False,
}
