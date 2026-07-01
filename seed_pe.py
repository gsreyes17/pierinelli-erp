# -*- coding: utf-8 -*-
# ============================================================
#  Pierinelli - SEED post-install (ejecutar con: odoo shell -d DB < seed_pe.py)
#  Configura contabilidad peruana (plan 'pe', IGV 18%, RUC) y genera datos
#  de ejemplo con IGV: clientes con RUC, proveedores, compras, ventas,
#  facturas (Factura), transferencias entre almacenes y oportunidades CRM.
#  Idempotente por version.
# ============================================================
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger('pierinelli_seed')
SEED_VERSION = '1'
LANG = 'es_419'

ICP = env['ir.config_parameter'].sudo()
if ICP.get_param('pierinelli.seed_pe_version') == SEED_VERSION:
    print('SEED ya aplicado (version %s), omitiendo.' % SEED_VERSION)
else:
    company = env.ref('base.main_company')
    company.country_id = env.ref('base.pe')

    # --- 1) Plan de cuentas peruano (registry ya cargado -> persiste) ---
    if company.chart_template != 'pe':
        env['account.chart.template'].try_loading('pe', company, install_demo=False)
        print('Plan contable PE cargado. IGV venta:', company.account_sale_tax_id.name)
    sale_tax = company.account_sale_tax_id
    purchase_tax = company.account_purchase_tax_id

    # --- 2) RUC de la compania ---
    ruc_type = env.ref('l10n_pe.it_RUC')
    dni_type = env.ref('l10n_pe.it_DNI', raise_if_not_found=False)
    company.partner_id.l10n_latam_identification_type_id = ruc_type
    company.partner_id.vat = '20131312955'

    # --- Utilidades ---
    def ruc_valido(base10):
        pesos = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        s = sum(int(d) * p for d, p in zip(base10, pesos))
        r = 11 - (s % 11)
        chk = {10: 0, 11: 1}.get(r, r)
        return base10 + str(chk)

    def prod(code):
        return env['product.product'].search([('default_code', '=', code)], limit=1)

    Partner = env['res.partner']
    Product = env['product.template']
    pe = env.ref('base.pe')

    # --- 3) Impuesto IGV en productos existentes ---
    existentes = Product.search([('default_code', '!=', False)])
    vals = {}
    if sale_tax:
        vals['taxes_id'] = [(6, 0, sale_tax.ids)]
    if purchase_tax:
        vals['supplier_taxes_id'] = [(6, 0, purchase_tax.ids)]
    if vals:
        existentes.write(vals)

    # --- 4) Catalogo ampliado (~24 productos mas) ---
    def C(x):
        return env.ref('pierinelli_data.categ_%s' % x).id

    catalogo = [
        ('Cuarcita Taj Mahal', 'CUA-TAJMAHAL', 'cuarcita', 980),
        ('Cuarcita Fusion', 'CUA-FUSION', 'cuarcita', 1050),
        ('Cuarcita Sea Pearl', 'CUA-SEAPEARL', 'cuarcita', 920),
        ('Granito Negro Absoluto', 'GRA-NEGROABS', 'granito', 720),
        ('Granito Blanco Dallas', 'GRA-DALLAS', 'granito', 560),
        ('Granito Verde Ubatuba', 'GRA-UBATUBA', 'granito', 640),
        ('Marmol Carrara', 'MAR-CARRARA', 'marmol', 1100),
        ('Marmol Calacatta', 'MAR-CALACATTA', 'marmol', 1800),
        ('Marmol Nero Marquina', 'MAR-MARQUINA', 'marmol', 1350),
        ('Marmol Emperador', 'MAR-EMPERADOR', 'marmol', 1250),
        ('Onix Blanco', 'ONX-BLANCO', 'onix', 1400),
        ('Onix Verde', 'ONX-VERDE', 'onix', 1500),
        ('Onix Miel', 'ONX-MIEL', 'onix', 1300),
        ('Sinterizada Calacatta Gold', 'SIN-CALGOLD', 'sinterizada', 1050),
        ('Sinterizada Sofia', 'SIN-SOFIA', 'sinterizada', 980),
        ('Sinterizada Nebbia', 'SIN-NEBBIA', 'sinterizada', 940),
        ('Porcelanico Gris Cemento', 'POR-GRISCEM', 'porcelanico', 320),
        ('Porcelanico Madera Roble', 'POR-ROBLE', 'porcelanico', 350),
        ('Porcelanico Marmol Look', 'POR-MARMOL', 'porcelanico', 380),
        ('Cuarzo Blanco Zeus', 'CRZ-ZEUS', 'cuarzo', 690),
        ('Cuarzo Gris Expo', 'CRZ-EXPO', 'cuarzo', 660),
        ('Solid Surface Corian Glacier White', 'SOL-GLACIER', 'solid_surface', 890),
        ('Solid Surface Corian Deep Nocturne', 'SOL-NOCTURNE', 'solid_surface', 950),
        ('Marmol Portoro Extra', 'MAR-PORTORO2', 'marmol', 1650),
    ]
    m2 = env.ref('uom.product_uom_square_meter')
    creados_prod = 0
    for name, code, cat, price in catalogo:
        if not prod(code):
            Product.create({
                'name': name, 'default_code': code, 'type': 'consu',
                'is_storable': True, 'categ_id': C(cat), 'uom_id': m2.id,
                'list_price': price,
                'taxes_id': [(6, 0, sale_tax.ids)] if sale_tax else False,
                'supplier_taxes_id': [(6, 0, purchase_tax.ids)] if purchase_tax else False,
            })
            creados_prod += 1
    print('Productos nuevos:', creados_prod)

    todos_prod = env['product.product'].search([('default_code', '!=', False)])

    # --- 5) Clientes con RUC ---
    nombres_cli = [
        'Constructora Andina Demo S.A.C.', 'Estudio Arquitectura Vela & Asociados',
        'Inmobiliaria Costa Verde S.A.C.', 'Disenos Interiores Lumen E.I.R.L.',
        'Constructora del Pacifico S.A.', 'Arq. Mariana Foppiani Estudio S.A.C.',
        'Grupo Inmobiliario Miraflores S.A.', 'Marmoleria San Isidro S.A.C.',
        'Proyectos Urbanos Lima Norte S.A.C.', 'Constructora Sur Andina S.A.C.',
        'Hotel Boutique Barranco S.A.C.', 'Cocinas & Espacios Premium S.A.C.',
        'Desarrollos Residenciales Surco S.A.', 'Estudio Arquitectonico Nova S.A.C.',
        'Constructora Trujillo Norte S.A.C.', 'Inversiones Arequipa Sur S.A.C.',
        'Remodelaciones Elite S.A.C.', 'Grupo Constructor Pacasmayo S.A.',
    ]
    ciudades = ['San Isidro - Lima', 'Miraflores - Lima', 'Surco - Lima',
                'Trujillo', 'Arequipa', 'San Borja - Lima']
    clientes = []
    for i, nombre in enumerate(nombres_cli):
        p = Partner.search([('name', '=', nombre)], limit=1)
        if not p:
            p = Partner.create({
                'name': nombre, 'is_company': True, 'lang': LANG,
                'country_id': pe.id, 'city': ciudades[i % len(ciudades)],
                'l10n_latam_identification_type_id': ruc_type.id,
                'vat': ruc_valido('20%08d' % (10200300 + i * 7)),
                'email': 'ventas%02d@cliente-demo.pe' % i,
                'customer_rank': 1,
            })
        clientes.append(p)
    print('Clientes:', len(clientes))

    # --- 6) Proveedores con RUC ---
    nombres_prov = [
        'Canteras del Sur Import S.A.C.', 'Neolith Peru Distribuidora S.A.C.',
        'Marmoles Italianos Import S.A.C.', 'Silestone Andina S.A.C.',
        'Corian Surfaces Peru S.A.C.',
    ]
    proveedores = []
    for i, nombre in enumerate(nombres_prov):
        p = Partner.search([('name', '=', nombre)], limit=1)
        if not p:
            p = Partner.create({
                'name': nombre, 'is_company': True, 'lang': LANG,
                'country_id': pe.id, 'city': 'Callao - Lima',
                'l10n_latam_identification_type_id': ruc_type.id,
                'vat': ruc_valido('20%08d' % (20500600 + i * 13)),
                'email': 'compras%02d@proveedor-demo.pe' % i,
                'supplier_rank': 1,
            })
        proveedores.append(p)
    print('Proveedores:', len(proveedores))

    # --- 7) Stock inicial en varios almacenes ---
    Quant = env['stock.quant']
    almacenes = {
        'UG': env.ref('stock.warehouse0'),
        'PRIN': env.ref('pierinelli_data.warehouse_principal', raise_if_not_found=False),
        'VES': env.ref('pierinelli_data.warehouse_ves', raise_if_not_found=False),
        'TRU': env.ref('pierinelli_data.warehouse_trujillo', raise_if_not_found=False),
        'AQP': env.ref('pierinelli_data.warehouse_arequipa', raise_if_not_found=False),
    }
    for idx, p in enumerate(todos_prod):
        for j, (code, wh) in enumerate(almacenes.items()):
            if not wh:
                continue
            qty = 40 + ((idx * 7 + j * 11) % 120)
            Quant._update_available_quantity(p, wh.lot_stock_id, qty)
    print('Stock repartido en almacenes.')

    # --- 8) Compras a proveedores (con IGV) ---
    PO = env['purchase.order']
    creados_po = 0
    for i, prov in enumerate(proveedores):
        tag = 'SEED-PO-%s' % prov.id
        if PO.search([('partner_ref', '=', tag)], limit=1):
            continue
        lineas = [todos_prod[(i * 3 + k) % len(todos_prod)] for k in range(3)]
        po = PO.create({
            'partner_id': prov.id,
            'partner_ref': tag,
            'order_line': [(0, 0, {
                'product_id': pr.id, 'product_qty': 20 + k * 10,
                'price_unit': pr.list_price * 0.55,
                'name': pr.name,
            }) for k, pr in enumerate(lineas)],
        })
        try:
            po.button_confirm()
            for pick in po.picking_ids:
                pick.action_assign()
                for mv in pick.move_ids:
                    mv.quantity = mv.product_uom_qty
                pick.move_ids.picked = True
                pick._action_done()
            creados_po += 1
        except Exception as e:
            _logger.warning('PO %s: %s', tag, e)
    print('Ordenes de compra:', creados_po)

    # --- 9) Ventas con IGV + facturas (Factura) ---
    SO = env['sale.order']
    factura = env.ref('l10n_pe.document_type01', raise_if_not_found=False)  # Factura
    warehouses_list = [w for w in almacenes.values() if w]
    creados_so = 0
    facturas = 0
    for i in range(45):
        tag = 'SEED-SO-%03d' % i
        if SO.search([('client_order_ref', '=', tag)], limit=1):
            continue
        cliente = clientes[i % len(clientes)]
        wh = warehouses_list[i % len(warehouses_list)]
        nlineas = 1 + (i % 3)
        lineas = [todos_prod[(i * 5 + k) % len(todos_prod)] for k in range(nlineas)]
        dias = (i * 7) % 150
        order = SO.create({
            'partner_id': cliente.id,
            'warehouse_id': wh.id,
            'client_order_ref': tag,
            'date_order': datetime.now() - timedelta(days=dias),
            'order_line': [(0, 0, {
                'product_id': pr.id,
                'product_uom_qty': 5 + ((i + k * 3) % 25),
            }) for k, pr in enumerate(lineas)],
        })
        order.action_confirm()
        # Entregar la mayoria
        if i % 5 != 0:
            for pick in order.picking_ids:
                if pick.state in ('done', 'cancel'):
                    continue
                pick.action_assign()
                for mv in pick.move_ids:
                    mv.quantity = mv.product_uom_qty
                pick.move_ids.picked = True
                try:
                    pick._action_done()
                except Exception:
                    pass
        # Facturar ~2/3 (Factura electronica con IGV)
        if i % 3 != 0:
            try:
                inv = order._create_invoices()
                if inv:
                    if factura:
                        inv.l10n_latam_document_type_id = factura.id
                    inv.action_post()
                    facturas += 1
            except Exception as e:
                _logger.warning('Factura SO %s: %s', tag, e)
        creados_so += 1
    print('Ventas nuevas:', creados_so, '| Facturas emitidas:', facturas)
    env.cr.commit()

    # --- 10) Transferencias entre almacenes ---
    prin = almacenes.get('PRIN')
    ug = almacenes.get('UG')
    if prin and ug:
        int_type = ug.int_type_id
        for k in range(3):
            pr = todos_prod[k]
            tagref = 'SEED-TR-%s' % pr.default_code
            if env['stock.picking'].search([('origin', '=', tagref)], limit=1):
                continue
            try:
                pick = env['stock.picking'].create({
                    'picking_type_id': int_type.id,
                    'location_id': prin.lot_stock_id.id,
                    'location_dest_id': ug.lot_stock_id.id,
                    'origin': tagref,
                    'move_ids': [(0, 0, {
                        'product_id': pr.id,
                        'product_uom_qty': 10, 'product_uom': pr.uom_id.id,
                        'location_id': prin.lot_stock_id.id,
                        'location_dest_id': ug.lot_stock_id.id,
                    })],
                })
                pick.action_confirm(); pick.action_assign()
                for mv in pick.move_ids:
                    mv.quantity = mv.product_uom_qty
                pick.move_ids.picked = True
                pick._action_done()
            except Exception as e:
                _logger.warning('Transferencia %s: %s', tagref, e)
    print('Transferencias entre almacenes creadas.')
    env.cr.commit()

    # --- 11) CRM ---
    Lead = env['crm.lead']
    stages = {s: env.ref('crm.stage_lead%d' % n)
              for n, s in enumerate(['new', 'qualified', 'proposition', 'won'], start=1)}
    temas = [
        ('Encimeras Marmol Portoro - Penthouse', 'proposition', 22500),
        ('Fachada cuarcita - Torre corporativa', 'qualified', 68000),
        ('Isla cocina Silestone - Depto modelo', 'new', 9800),
        ('Pisos porcelanico - Obra Arequipa', 'proposition', 41000),
        ('Bano onix retroiluminado - Casa playa', 'won', 15600),
        ('Barra granito - Restaurante Barranco', 'qualified', 12300),
        ('Revestimiento sinterizada - Hotel', 'proposition', 54000),
        ('Marmol Calacatta - Lobby edificio', 'new', 33000),
        ('Solid Surface - Clinica dental', 'qualified', 8700),
        ('Cuarzo - Cocina residencial Surco', 'won', 11200),
        ('Onix verde - Spa boutique', 'new', 19800),
        ('Porcelanico gran formato - Showroom', 'proposition', 26500),
    ]
    creados_lead = 0
    for i, (name, stage, rev) in enumerate(temas):
        if not Lead.search([('name', '=', name)], limit=1):
            Lead.create({
                'name': name, 'type': 'opportunity',
                'partner_id': clientes[i % len(clientes)].id,
                'expected_revenue': rev, 'stage_id': stages[stage].id,
                'email_from': clientes[i % len(clientes)].email,
            })
            creados_lead += 1
    print('Oportunidades CRM nuevas:', creados_lead)

    ICP.set_param('pierinelli.seed_pe_version', SEED_VERSION)
    env.cr.commit()
    print('SEED COMPLETO (version %s).' % SEED_VERSION)
