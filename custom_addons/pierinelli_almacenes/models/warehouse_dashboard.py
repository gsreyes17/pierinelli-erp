# -*- coding: utf-8 -*-
"""
Servicio de datos para el tablero 'Panorama de Almacenes'.

Calcula, por almacen, el stock en m2, el valor de inventario (cantidad x costo),
el numero de productos distintos y una ocupacion relativa (respecto al almacen
con mas stock). Tambien devuelve el ranking de productos con mayor stock y las
coordenadas para ubicar cada sede en el mapa del Peru.
"""
from odoo import api, models


# Posicion de cada sede en el SVG del mapa (coordenadas 0..100 en x/y sobre el
# viewBox del mapa del Peru). Se identifican por el codigo de almacen.
# Posiciones sobre el mapa (viewBox 0 0 260 380). x/y = pin en la ciudad real
# (proyeccion lon/lat -> SVG); lx/ly = donde va la etiqueta (las 3 sedes de
# Lima comparten ciudad, asi que sus etiquetas se separan con lineas guia).
SEDE_GEO = {
    'UG':   {'ciudad': 'Miraflores, Lima',  'x': 90.5,  'y': 250.5, 'lx': 26,  'ly': 226},
    'PRIN': {'ciudad': 'Zarate, Lima',      'x': 93.5,  'y': 246.0, 'lx': 26,  'ly': 246},
    'VES':  {'ciudad': 'Villa El Salvador', 'x': 91.5,  'y': 255.5, 'lx': 26,  'ly': 266},
    'TRU':  {'ciudad': 'Trujillo',          'x': 50.6,  'y': 169.5, 'lx': 10,  'ly': 152},
    'AQP':  {'ciudad': 'Arequipa',          'x': 203.3, 'y': 338.6, 'lx': 136, 'ly': 318},
}


class WarehouseDashboard(models.AbstractModel):
    _name = 'pierinelli.warehouse.dashboard'
    _description = 'Datos del Panorama de Almacenes'

    @api.model
    def get_dashboard_data(self):
        Quant = self.env['stock.quant']
        warehouses = self.env['stock.warehouse'].search([])
        sedes = []
        max_m2 = 0.0
        total_m2 = total_valor = 0.0

        for w in warehouses:
            loc = w.lot_stock_id
            quants = Quant.search([
                ('location_id', 'child_of', loc.id),
                ('quantity', '>', 0),
            ])
            m2 = sum(quants.mapped('quantity'))
            valor = sum(q.quantity * (q.product_id.standard_price or 0.0) for q in quants)
            prods = len(set(quants.mapped('product_id').ids))
            geo = SEDE_GEO.get(w.code, {'ciudad': '', 'x': 130, 'y': 190,
                                        'lx': 100, 'ly': 170})
            sedes.append({
                'id': w.id,
                'code': w.code,
                'name': w.name,
                'ciudad': geo['ciudad'],
                'x': geo['x'],
                'y': geo['y'],
                'lx': geo['lx'],
                'ly': geo['ly'],
                'm2': round(m2, 1),
                'valor': round(valor, 2),
                'productos': prods,
            })
            max_m2 = max(max_m2, m2)
            total_m2 += m2
            total_valor += valor

        # ocupacion relativa (%) respecto a la sede con mas stock
        for s in sedes:
            s['ocupacion'] = round((s['m2'] / max_m2 * 100.0), 0) if max_m2 else 0.0

        # Ranking de productos por stock total (con imagen).
        # qty_available es un campo calculado NO almacenado: no se puede usar en
        # el dominio/orden SQL. Se leen los productos almacenables y se ordena en
        # Python por su cantidad disponible.
        candidatos = self.env['product.product'].search([('is_storable', '=', True)])
        candidatos = candidatos.filtered(lambda p: p.qty_available > 0)
        top = candidatos.sorted(key=lambda p: p.qty_available, reverse=True)[:8]
        productos = []
        for p in top:
            qty = p.qty_available
            productos.append({
                'id': p.id,
                'code': p.default_code or '',
                'name': p.name,
                'qty': round(qty, 1),
                'valor': round(qty * (p.standard_price or 0.0), 2),
                'categoria': p.categ_id.name or '',
                # URL de la imagen del producto (se sirve por el web/image)
                'image': '/web/image/product.product/%s/image_128' % p.id,
            })

        return {
            'sedes': sedes,
            'productos': productos,
            'totales': {
                'sedes': len(sedes),
                'm2': round(total_m2, 1),
                'valor': round(total_valor, 2),
                'productos': len(top),
            },
            'moneda': self.env.company.currency_id.symbol or 'S/',
        }
