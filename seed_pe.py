# -*- coding: utf-8 -*-
# ============================================================
#  Pierinelli - SEED post-install (ejecutar con: odoo shell -d DB < seed_pe.py)
#  Configura contabilidad peruana (plan 'pe', IGV 18%, RUC) y genera datos
#  de ejemplo con IGV: clientes con RUC, proveedores, compras + facturas de
#  proveedor, cotizaciones, ventas, facturas de cliente, pagos registrados y
#  transferencias entre almacenes. Idempotente por version.
# ============================================================
from datetime import datetime, timedelta
import base64
import json as _json
import logging
from odoo.tools import file_open

_logger = logging.getLogger('pierinelli_seed')
SEED_VERSION = '16'
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

    # --- 4) Catalogo REAL (desde products.json de la web) + imagenes ---
    def C(x):
        return env.ref('pierinelli_data.categ_%s' % x).id

    m2 = env.ref('uom.product_uom_square_meter')
    try:
        with file_open('pierinelli_data/static/products.json', 'rb') as f:
            catalogo = _json.loads(f.read().decode('utf-8'))
    except Exception as e:
        catalogo = []
        _logger.warning('products.json no encontrado: %s', e)

    # Familias naturales: cada plancha es unica (foto individual).
    NATURALES = {'marmol', 'granito', 'cuarcita', 'onix'}

    creados_prod = 0
    con_imagen = 0
    for it in catalogo:
        p = prod(it['code'])
        if p:
            tmpl = p.product_tmpl_id
        else:
            tmpl = Product.create({
                'name': it['name'], 'default_code': it['code'], 'type': 'consu',
                'is_storable': True, 'categ_id': C(it['categ']), 'uom_id': m2.id,
                # Modelo V2: cada plancha es un lote de su producto
                'tracking': 'lot',
                'tipo_material': ('natural' if it['categ'] in NATURALES
                                  else 'artificial'),
                'list_price': it['price'],
                'standard_price': round(it['price'] * 0.6, 2),  # costo -> valorizacion de inventario
                'taxes_id': [(6, 0, sale_tax.ids)] if sale_tax else False,
                'supplier_taxes_id': [(6, 0, purchase_tax.ids)] if purchase_tax else False,
            })
            creados_prod += 1
        # Imagen real del producto
        try:
            with file_open('pierinelli_data/static/img/products/%s' % it['image'], 'rb') as f:
                tmpl.image_1920 = base64.b64encode(f.read())
                con_imagen += 1
        except Exception as e:
            _logger.warning('Imagen %s: %s', it['code'], e)
        # Commit por producto -> transacciones pequenas (evita caidas SSL en Render)
        env.cr.commit()
    print('Productos catalogo:', creados_prod, '| con imagen:', con_imagen,
          '| total JSON:', len(catalogo))

    todos_prod = env['product.product'].search([('default_code', '!=', False)])
    env.cr.commit()

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
    # Terminos de pago (para vencimientos y antiguedad de saldos)
    terms = [env.ref(x, raise_if_not_found=False) for x in (
        'account.account_payment_term_immediate',
        'account.account_payment_term_30days',
        'account.account_payment_term_45days')]
    terms = [t for t in terms if t]
    term_30 = env.ref('account.account_payment_term_30days', raise_if_not_found=False)

    clientes = []
    for i, nombre in enumerate(nombres_cli):
        p = Partner.search([('name', '=', nombre)], limit=1)
        if not p:
            vals = {
                'name': nombre, 'is_company': True, 'lang': LANG,
                'country_id': pe.id, 'city': ciudades[i % len(ciudades)],
                'l10n_latam_identification_type_id': ruc_type.id,
                'vat': ruc_valido('20%08d' % (10200300 + i * 7)),
                'email': 'ventas%02d@cliente-demo.pe' % i,
                'customer_rank': 1,
            }
            if terms:
                vals['property_payment_term_id'] = terms[i % len(terms)].id
            p = Partner.create(vals)
        clientes.append(p)
    env.cr.commit()
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
            vals = {
                'name': nombre, 'is_company': True, 'lang': LANG,
                'country_id': pe.id, 'city': 'Callao - Lima',
                'l10n_latam_identification_type_id': ruc_type.id,
                'vat': ruc_valido('20%08d' % (20500600 + i * 13)),
                'email': 'compras%02d@proveedor-demo.pe' % i,
                'supplier_rank': 1,
            }
            if term_30:
                vals['property_supplier_payment_term_id'] = term_30.id
            p = Partner.create(vals)
        proveedores.append(p)
    env.cr.commit()
    print('Proveedores:', len(proveedores))

    # --- 7) Stock inicial: PLANCHAS con codigo interno en cada almacen ---
    # Modelo V2: cada plancha fisica es un lote con medidas, ubicacion
    # referencial y ficha propia. El stock del producto = suma de sus planchas.
    Quant = env['stock.quant']
    Lot = env['stock.lot']
    almacenes = {
        'UG': env.ref('stock.warehouse0'),
        'PRIN': env.ref('pierinelli_data.warehouse_principal', raise_if_not_found=False),
        'VES': env.ref('pierinelli_data.warehouse_ves', raise_if_not_found=False),
        'TRU': env.ref('pierinelli_data.warehouse_trujillo', raise_if_not_found=False),
        'AQP': env.ref('pierinelli_data.warehouse_arequipa', raise_if_not_found=False),
    }
    # Formatos tipicos de plancha (largo, alto) en metros
    DIMS = [(3.40, 1.65), (3.20, 1.60), (3.00, 1.50),
            (3.35, 1.70), (2.90, 1.55), (3.10, 1.85)]
    ZONAS = ['Zona A · Rack 1', 'Zona A · Rack 2', 'Zona B · Rack 1',
             'Zona B · Rack 3', 'Patio · Caballete 1', 'Showroom · Caballete 2']
    total_planchas = 0
    if not Lot.search([('ref_importacion', '=like', 'IMP-SEED%')], limit=1):
        for idx, p in enumerate(todos_prod):
            if not p.is_storable or p.tracking != 'lot':
                continue
            tmpl = p.product_tmpl_id
            for j, (code, wh) in enumerate(almacenes.items()):
                if not wh:
                    continue
                n = 1 + ((idx + j) % 2)      # 1-2 planchas por sede
                # Fecha de llegada repartida (algunas > 1 anio -> Hueso)
                dias_atras = 20 + ((idx * 13 + j * 47) % 420)
                fecha_llegada = (datetime.now() - timedelta(days=dias_atras)).date()
                codigos = Lot.siguiente_codigo(p, count=n, fecha=fecha_llegada)
                for c in codigos:
                    largo, alto = DIMS[(idx + j + total_planchas) % len(DIMS)]
                    m2v = round(largo * alto, 2)
                    lot = Lot.create({
                        'name': c, 'product_id': p.id,
                        'company_id': company.id,
                        'largo': largo, 'alto': alto, 'espesor': 2.0,
                        'm2_neto': m2v,
                        'ubicacion_ref': ZONAS[(idx * 3 + j) % len(ZONAS)],
                        'ref_importacion': 'IMP-SEED-%s' % fecha_llegada.strftime('%m%y'),
                        'fecha_ingreso': fecha_llegada,
                    })
                    # Naturales: foto por plancha (en demo, la del producto;
                    # en produccion cada plancha lleva su foto real)
                    if tmpl.tipo_material == 'natural' and tmpl.image_1920:
                        lot.image_1920 = tmpl.image_1920
                    Quant._update_available_quantity(
                        p, wh.lot_stock_id, m2v, lot_id=lot)
                    total_planchas += 1
            env.cr.commit()
    print('Planchas generadas:', total_planchas)

    # --- 8) Compras a proveedores (con IGV) + facturas de proveedor ---
    PO = env['purchase.order']
    factura = env.ref('l10n_pe.document_type01', raise_if_not_found=False)  # Factura
    creados_po = 0
    bills = 0
    for i, prov in enumerate(proveedores):
        tag = 'SEED-PO-%s' % prov.id
        if PO.search([('partner_ref', '=', tag)], limit=1):
            continue
        lineas = [todos_prod[(i * 3 + k) % len(todos_prod)] for k in range(3)]
        # Cada linea pide N planchas del formato 3.20 x 1.60 (5.12 m² c/u):
        # la cantidad de la orden = suma exacta de las planchas a recibir.
        PLANCHA_M2 = 5.12
        n_planchas_linea = [2 + k for k in range(3)]        # 2, 3, 4 planchas
        po = PO.create({
            'partner_id': prov.id,
            'partner_ref': tag,
            'order_line': [(0, 0, {
                'product_id': pr.id,
                'product_qty': round(PLANCHA_M2 * n_planchas_linea[k], 2),
                'price_unit': pr.list_price * 0.55,
                'name': pr.name,
            }) for k, pr in enumerate(lineas)],
        })
        try:
            po.button_confirm()
            for pick in po.picking_ids:
                pick.action_assign()
                # La recepcion da de alta las planchas: un lote por plancha
                for mv in pick.move_ids:
                    n = max(1, int(round(mv.product_uom_qty / PLANCHA_M2)))
                    codigos = Lot.siguiente_codigo(mv.product_id, count=n)
                    mv.move_line_ids = [(5, 0, 0)] + [(0, 0, {
                        'product_id': mv.product_id.id,
                        'lot_name': c,
                        'quantity': PLANCHA_M2,
                        'location_id': mv.location_id.id,
                        'location_dest_id': mv.location_dest_id.id,
                    }) for c in codigos]
                pick.move_ids.picked = True
                pick._action_done()
                # Completar la ficha de las planchas recien creadas
                for ml in pick.move_ids.move_line_ids:
                    if ml.lot_id and not ml.lot_id.largo:
                        ml.lot_id.write({
                            'largo': 3.20, 'alto': 1.60, 'espesor': 2.0,
                            'm2_neto': PLANCHA_M2,
                            'ref_importacion': po.name,
                            'ubicacion_ref': 'Zona Recepcion',
                        })
                        tmpl = ml.lot_id.product_id.product_tmpl_id
                        if tmpl.tipo_material == 'natural' and tmpl.image_1920:
                            ml.lot_id.image_1920 = tmpl.image_1920
            creados_po += 1
            # Factura de proveedor (cuenta por pagar / gasto)
            try:
                po.action_create_invoice()
                bill = po.invoice_ids[:1]
                if bill:
                    bill.invoice_date = (datetime.now() - timedelta(days=20 + i * 3)).date()
                    if factura and 'l10n_latam_document_type_id' in bill._fields:
                        bill.l10n_latam_document_type_id = factura.id
                    if 'l10n_latam_document_number' in bill._fields:
                        bill.l10n_latam_document_number = 'F%03d-%08d' % (i + 1, 1000 + i)
                    bill.action_post()
                    bills += 1
            except Exception as e:
                _logger.warning('Factura proveedor %s: %s', tag, e)
        except Exception as e:
            _logger.warning('PO %s: %s', tag, e)
    print('Ordenes de compra:', creados_po, '| Facturas de proveedor:', bills)

    # --- 9) Cotizaciones, ventas, facturas (IGV), pagos y analitica por obra ---
    SO = env['sale.order']
    warehouses_list = [w for w in almacenes.values() if w]

    # Analitica: plan "Obras / Proyectos" + cuentas por obra (rentabilidad)
    AAP = env['account.analytic.plan']
    AAA = env['account.analytic.account']
    plan = AAP.search([('name', '=', 'Obras / Proyectos')], limit=1)
    if not plan:
        plan = AAP.create({'name': 'Obras / Proyectos'})
    obras_nombres = [
        'Obra Torre San Isidro', 'Proyecto Casa Playa Asia',
        'Remodelacion Hotel Barranco', 'Edificio Corporativo Surco',
        'Showroom Miraflores', 'Condominio Trujillo',
    ]
    obras = []
    for on in obras_nombres:
        a = AAA.search([('name', '=', on)], limit=1)
        if not a:
            a = AAA.create({'name': on, 'plan_id': plan.id})
        obras.append(a)

    creados_so = 0
    cotizaciones = 0
    facturas = 0
    pagos = 0
    for i in range(48):
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
                # A escala de plancha: 4-11 m² por linea (1-2 planchas)
                'product_uom_qty': 4 + ((i + k * 3) % 8),
                'analytic_distribution': ({str(obras[i % len(obras)].id): 100}
                                          if obras else False),
            }) for k, pr in enumerate(lineas)],
        })
        creados_so += 1
        # ~1 de cada 5 queda como COTIZACION (borrador / enviada)
        if i % 5 == 0:
            if i % 2 == 0:
                try:
                    order.action_quotation_sent()
                except Exception:
                    pass
            cotizaciones += 1
            continue
        # El resto se confirma (pedido de venta)
        order.action_confirm()
        order.date_order = datetime.now() - timedelta(days=dias)  # confirmar la sobrescribe
        # Entregar la mayoria. Con planchas (lotes) la reserva automatica
        # elige que planchas salen; solo validamos si reservo completo.
        if i % 4 != 0:
            for pick in order.picking_ids:
                if pick.state in ('done', 'cancel'):
                    continue
                pick.action_assign()
                if pick.state != 'assigned':
                    continue    # sin planchas suficientes -> queda pendiente
                pick.move_ids.picked = True
                try:
                    pick._action_done()
                except Exception:
                    pass
        # Facturar ~2/3 con IGV
        if i % 3 != 0:
            try:
                inv = order._create_invoices()
                if inv:
                    if factura:
                        inv.l10n_latam_document_type_id = factura.id
                    inv.action_post()
                    facturas += 1
                    # Registrar pago en ~la mitad de las facturas
                    if i % 2 == 0:
                        try:
                            wiz = env['account.payment.register'].with_context(
                                active_model='account.move', active_ids=inv.ids
                            ).create({})
                            wiz.action_create_payments()
                            pagos += 1
                        except Exception as e:
                            _logger.warning('Pago SO %s: %s', tag, e)
            except Exception as e:
                _logger.warning('Factura SO %s: %s', tag, e)
    print('Ventas:', creados_so, '| Cotizaciones:', cotizaciones,
          '| Facturas:', facturas, '| Pagos:', pagos)
    env.cr.commit()

    # --- 9b) Caso "Madre Selva": listas de precios, servicios, CRM y cotizacion modelo ---
    # Habilitar listas de precios en la interfaz
    gpl = env.ref('product.group_product_pricelist', raise_if_not_found=False)
    if gpl:
        env.ref('base.group_user').write({'implied_ids': [(4, gpl.id)]})

    Pricelist = env['product.pricelist']
    PLItem = env['product.pricelist.item']

    def get_pricelist(name, percent=None):
        pl = Pricelist.search([('name', '=', name)], limit=1)
        if not pl:
            pl = Pricelist.create({'name': name, 'currency_id': company.currency_id.id})
            if percent:
                PLItem.create({'pricelist_id': pl.id, 'applied_on': '3_global',
                               'compute_price': 'percentage', 'percent_price': percent})
        return pl

    get_pricelist('Publico')
    get_pricelist('Profesionales (-12%)', percent=12)
    pl_proy = get_pricelist('Proyectos por volumen', percent=18)
    for c in clientes[:6]:
        c.property_product_pricelist = pl_proy.id

    # Servicios (corte, instalacion, flete)
    for nombre, code, precio in [
            ('Corte y fabricacion de encimeras a medida', 'SRV-CORTE', 1150),
            ('Instalacion en obra + flete', 'SRV-INSTAL', 6900),
            ('Flete a obra', 'SRV-FLETE', 850)]:
        if not prod(code):
            Product.create({'name': nombre, 'default_code': code, 'type': 'service',
                            'list_price': precio, 'invoice_policy': 'order',
                            'taxes_id': [(6, 0, sale_tax.ids)] if sale_tax else False})
    env.cr.commit()

    # Cliente del caso: Constructora Altavista SAC + arquitecta
    altavista = Partner.search([('name', '=', 'Constructora Altavista SAC')], limit=1)
    if not altavista:
        altavista = Partner.create({
            'name': 'Constructora Altavista SAC', 'is_company': True, 'lang': LANG,
            'country_id': pe.id, 'city': 'Surco - Lima', 'street': 'Av. El Derby 254, Surco',
            'l10n_latam_identification_type_id': ruc_type.id, 'vat': ruc_valido('2051234567'),
            'email': 'proyectos@altavista.pe', 'customer_rank': 1,
            'property_product_pricelist': pl_proy.id,
            'child_ids': [(0, 0, {'name': 'Maria Fernanda Riva', 'function': 'Arquitecta',
                                  'email': 'mf.riva@altavista.pe'})],
        })

    # CRM: embudo con la oportunidad heroe "Madre Selva"
    if 'crm.lead' in env:
        Lead = env['crm.lead']
        st = {s: env.ref('crm.stage_lead%d' % n, raise_if_not_found=False)
              for n, s in enumerate(['new', 'qualified', 'proposition', 'won'], 1)}
        adm = env.ref('base.user_admin', raise_if_not_found=False)
        crm_temas = [
            ('Encimeras Madre Selva - 12 dptos', altavista, 96000, 'qualified'),
            ('Fachada porcelanico - local Surquillo', clientes[1], 45000, 'new'),
            ('Piso marmol - lobby San Isidro', clientes[2], 22000, 'proposition'),
            ('Casa de playa - porcelanico exterior', clientes[3], 45000, 'new'),
            ('Hotel boutique Cusco - banos', clientes[4], 169000, 'qualified'),
            ('Torre Aurora - areas comunes', clientes[5], 87000, 'proposition'),
            ('Bano principal - casa La Molina', clientes[6], 18000, 'new'),
            ('Encimeras cuarzo - depto modelo', clientes[7], 15600, 'won'),
        ]
        for name, partner, rev, stage in crm_temas:
            if not Lead.search([('name', '=', name)], limit=1):
                v = {'name': name, 'type': 'opportunity', 'partner_id': partner.id,
                     'expected_revenue': rev, 'email_from': partner.email}
                if st.get(stage):
                    v['stage_id'] = st[stage].id
                if adm:
                    v['user_id'] = adm.id
                Lead.create(v)
        env.cr.commit()
        print('CRM: embudo con oportunidad Madre Selva cargado.')

    # Cotizacion modelo "Madre Selva" con secciones + factura de anticipo 50%
    enigma = prod('CUA-CUARCITAENIGMA')
    corte = prod('SRV-CORTE')
    instal = prod('SRV-INSTAL')
    if enigma and not SO.search([('client_order_ref', '=', 'MADRE-SELVA')], limit=1):
        lineas_ms = [
            (0, 0, {'display_type': 'line_section', 'name': 'MATERIALES'}),
            (0, 0, {'product_id': enigma.id, 'product_uom_qty': 48}),
            (0, 0, {'display_type': 'line_section', 'name': 'SERVICIOS'}),
        ]
        if corte:
            lineas_ms.append((0, 0, {'product_id': corte.id, 'product_uom_qty': 12}))
        if instal:
            lineas_ms.append((0, 0, {'product_id': instal.id, 'product_uom_qty': 1}))
        ug_wh = almacenes.get('UG')
        try:
            ms = SO.create({
                'partner_id': altavista.id,
                'warehouse_id': ug_wh.id if ug_wh else False,
                'client_order_ref': 'MADRE-SELVA', 'pricelist_id': pl_proy.id,
                'order_line': lineas_ms,
            })
            ms.action_confirm()
            wiz = env['sale.advance.payment.inv'].with_context(
                active_model='sale.order', active_ids=ms.ids, active_id=ms.id
            ).create({'advance_payment_method': 'percentage', 'amount': 50})
            wiz.create_invoices()
            inv = ms.invoice_ids[:1]
            if inv:
                if factura:
                    inv.l10n_latam_document_type_id = factura.id
                inv.action_post()
            print('Cotizacion Madre Selva + anticipo 50% creados.')
        except Exception as e:
            _logger.warning('Madre Selva: %s', e)
        env.cr.commit()

    # --- 9c) Historial de ventas 12 meses (para los graficos de Ventas -> Informes) ---
    prod_venta = todos_prod.filtered(lambda p: p.is_storable)
    if prod_venta:
        hist = 0
        for mes in range(12):            # 12 meses hacia atras
            for k in range(7):           # ~7 ventas por mes
                tag = 'HIST-%02d-%d' % (mes, k)
                if SO.search([('client_order_ref', '=', tag)], limit=1):
                    continue
                cliente = clientes[(mes * 7 + k) % len(clientes)]
                wh = warehouses_list[(mes + k) % len(warehouses_list)]
                nl = 1 + ((mes + k) % 3)
                lineas = [prod_venta[(mes * 5 + k * 3 + j) % len(prod_venta)]
                          for j in range(nl)]
                # crecimiento suave + variacion por mes
                base_qty = 4 + (mes % 6) * 2
                fecha = datetime.now() - timedelta(days=mes * 30 + k * 4 + 2)
                try:
                    order = SO.create({
                        'partner_id': cliente.id, 'warehouse_id': wh.id,
                        'client_order_ref': tag, 'date_order': fecha,
                        'order_line': [(0, 0, {
                            'product_id': pr.id,
                            'product_uom_qty': base_qty + ((mes + k + j) % 18),
                        }) for j, pr in enumerate(lineas)],
                    })
                    order.action_confirm()
                    order.date_order = fecha  # confirmar sobrescribe la fecha -> la fijamos
                    hist += 1
                except Exception as e:
                    _logger.warning('Hist venta %s: %s', tag, e)
            env.cr.commit()
        print('Historial de ventas (12 meses):', hist)

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
                if pick.state != 'assigned':
                    continue    # sin planchas en PRIN para trasladar
                pick.move_ids.picked = True
                pick._action_done()
            except Exception as e:
                _logger.warning('Transferencia %s: %s', tagref, e)
    print('Transferencias entre almacenes creadas.')
    env.cr.commit()

    # --- 11) Usuarios de ejemplo por rol (referencia de permisos) ---
    Users = env['res.users']

    def grp(*xmlids):
        ids = []
        for x in xmlids:
            g = env.ref(x, raise_if_not_found=False)
            if g:
                ids.append(g.id)
        return ids

    usuarios = [
        ('Gerente General', 'gerente', grp(
            'base.group_user', 'sales_team.group_sale_manager',
            'stock.group_stock_manager', 'purchase.group_purchase_manager',
            'account.group_account_manager')),
        ('Vendedor Showroom', 'vendedor', grp(
            'base.group_user', 'sales_team.group_sale_salesman')),
        ('Almacenero', 'almacen', grp(
            'base.group_user', 'stock.group_stock_user')),
        ('Comprador', 'compras', grp(
            'base.group_user', 'purchase.group_purchase_user')),
        ('Contadora', 'contabilidad', grp(
            'base.group_user', 'account.group_account_user')),
        # --- Personas del caso "Madre Selva" (para las capturas del manual) ---
        ('Valeria Campos', 'valeria@pierinelli.com', grp(
            'base.group_user', 'sales_team.group_sale_salesman')),
        ('Diego Torres', 'diego@pierinelli.com', grp(
            'base.group_user', 'sales_team.group_sale_salesman')),
        ('Carlos Ramos', 'carlos@pierinelli.com', grp(
            'base.group_user', 'stock.group_stock_user')),
        ('Rosa Delgado', 'rosa@pierinelli.com', grp(
            'base.group_user', 'account.group_account_user')),
        ('Jorge Pierinelli', 'jorge@pierinelli.com', grp(
            'base.group_user', 'sales_team.group_sale_manager',
            'stock.group_stock_manager', 'purchase.group_purchase_manager',
            'account.group_account_manager')),
    ]
    creados_user = 0
    for nombre, login, gids in usuarios:
        if Users.search([('login', '=', login)], limit=1):
            continue
        try:
            Users.with_context(no_reset_password=True).create({
                'name': nombre, 'login': login, 'password': 'pierinelli',
                'lang': LANG, 'group_ids': [(6, 0, gids)],
            })
            creados_user += 1
        except Exception as e:
            _logger.warning('Usuario %s: %s', login, e)
    print('Usuarios de ejemplo:', creados_user)
    # Al iniciar sesion, ir a la GRILLA DE APPS (no a la primera app / Discuss)
    if 'is_redirect_home' in env['res.users']._fields:
        env['res.users'].search([('share', '=', False)]).write(
            {'is_redirect_home': True})
        print('Redireccion al menu de apps activada para usuarios internos.')
    env.cr.commit()

    # --- 11b) Asesores reales en los pedidos (antes todo era OdooBot) ---
    asesores = Users.search([('login', 'in', [
        'valeria@pierinelli.com', 'diego@pierinelli.com', 'vendedor'])])
    if asesores:
        pedidos_seed = SO.search([('client_order_ref', '!=', False)])
        for n, so in enumerate(pedidos_seed):
            so.user_id = asesores[n % len(asesores)]
        print('Asesores asignados a %d pedidos.' % len(pedidos_seed))
    env.cr.commit()

    # --- 11c) Reservas comerciales de muestra (regla de los 7 dias) ---
    libres = Lot.search([
        ('m2_disponible', '>', 0), ('cliente_reserva_id', '=', False),
        ('largo', '>', 0)], limit=4)
    hoy = datetime.now().date()
    for n, plancha in enumerate(libres):
        plancha.write({
            'cliente_reserva_id': clientes[n % len(clientes)].id,
            'asesor_id': asesores[n % len(asesores)].id if asesores else False,
            'reserva_inicio': hoy - timedelta(days=n),
            'reserva_fin': hoy + timedelta(days=7 - n),
        })
    print('Reservas de muestra:', len(libres))

    # --- 11d) Condicion Hueso: marcar lo que lleva mas de 1 anio ---
    Lot._cron_marcar_hueso()
    huesos = Lot.search_count([('condicion', '=', 'hueso')])
    print('Planchas en condicion Hueso:', huesos)
    env.cr.commit()

    # --- 11e) Asiento de APERTURA de existencias ---
    # Las planchas iniciales del seed entran por ajuste directo de stock (sin
    # asiento). Con valorizacion en tiempo real, las ventas SI acreditan la
    # cuenta 201 (Mercaderias), asi que sin apertura quedaria negativa. Este
    # asiento deja 201 = valor fisico del inventario (contra Capital).
    AM = env['account.move']
    if not AM.search([('ref', '=', 'SEED-APERTURA-EXISTENCIAS')], limit=1):
        Acc = env['account.account']
        cta_merc = Acc.search([('code', '=like', '2011%')], limit=1)
        cta_capital = Acc.search([('code', '=like', '5011%')], limit=1)
        diario_gral = env['account.journal'].search(
            [('type', '=', 'general')], limit=1)
        quants_int = env['stock.quant'].search(
            [('location_id.usage', '=', 'internal')])
        valor_fisico = sum(q.quantity * q.product_id.standard_price
                           for q in quants_int)
        mls_201 = env['account.move.line'].search(
            [('account_id.code', '=like', '201%'),
             ('parent_state', '=', 'posted')])
        apertura = round(valor_fisico - sum(mls_201.mapped('balance')), 2)
        if cta_merc and cta_capital and diario_gral and apertura > 0:
            asiento = AM.create({
                'move_type': 'entry',
                'journal_id': diario_gral.id,
                'ref': 'SEED-APERTURA-EXISTENCIAS',
                'date': (datetime.now() - timedelta(days=430)).date(),
                'line_ids': [
                    (0, 0, {'account_id': cta_merc.id,
                            'name': 'Apertura de existencias (planchas)',
                            'debit': apertura, 'credit': 0.0}),
                    (0, 0, {'account_id': cta_capital.id,
                            'name': 'Apertura de existencias (planchas)',
                            'debit': 0.0, 'credit': apertura}),
                ],
            })
            asiento.action_post()
            print('Apertura de existencias: S/ %.2f' % apertura)
    env.cr.commit()

    # --- 11f) Tipos de cambio (SUNAT / Corporativa) de muestra ---
    TC = env['pierinelli.tipo.cambio']
    if not TC.search([], limit=1):
        hoy_tc = datetime.now().date()
        for dias, (s_c, s_v), corp in [
                (2, (3.712, 3.721), 3.75),
                (1, (3.718, 3.727), 3.76),
                (0, (3.721, 3.730), 3.76)]:
            f = hoy_tc - timedelta(days=dias)
            TC.create({'fecha': f, 'origen': 'sunat',
                       'compra': s_c, 'venta': s_v})
            TC.create({'fecha': f, 'origen': 'corporativa',
                       'venta': corp,
                       'notas': 'Tasa comercial Pierinelli'})
        print('Tipos de cambio de muestra cargados.')

    # --- 11g) Plantillas de asientos contables de muestra ---
    Plantilla = env['pierinelli.plantilla.asiento']
    if not Plantilla.search([], limit=1):
        Acc = env['account.account']

        def cta(code):
            return Acc.search([('code', '=like', code + '%')], limit=1)

        diario_g = env['account.journal'].search(
            [('type', '=', 'general')], limit=1)
        plantillas_demo = [
            ('Planilla mensual', 'Sueldos del mes contra cuentas por pagar', [
                ('6211', 'Sueldos y salarios', 'debe', 'porcentaje', 100),
                ('4031', 'EsSalud 9%', 'debe', 'porcentaje', 9),
                ('4111', 'Remuneraciones por pagar', 'haber', 'porcentaje', 100),
                ('4031', 'Tributos por pagar', 'haber', 'porcentaje', 9),
            ]),
            ('Depreciacion mensual', 'Depreciacion de activos del mes', [
                ('6811', 'Depreciacion del periodo', 'debe', 'porcentaje', 100),
                ('3911', 'Depreciacion acumulada', 'haber', 'porcentaje', 100),
            ]),
        ]
        creadas_pl = 0
        for nombre, desc, lineas_pl in plantillas_demo:
            lineas_ok = []
            for code, glosa, lado, modo, valor in lineas_pl:
                cuenta = cta(code)
                if cuenta:
                    lineas_ok.append((0, 0, {
                        'account_id': cuenta.id, 'name': glosa,
                        'lado': lado, 'modo': modo, 'valor': valor}))
            if diario_g and len(lineas_ok) >= 2:
                Plantilla.create({'name': nombre, 'descripcion': desc,
                                  'journal_id': diario_g.id,
                                  'linea_ids': lineas_ok})
                creadas_pl += 1
        print('Plantillas de asientos:', creadas_pl)
    env.cr.commit()

    # --- 12) Trazabilidad: material PADRE (placa) -> HIJOS (piezas) con lote ---
    if 'mrp.production' in env:
        BoM = env['mrp.bom']
        MO = env['mrp.production']
        Lot = env['stock.lot']
        unidad = env.ref('uom.product_uom_unit')
        ubic = env.ref('stock.warehouse0').lot_stock_id
        ejemplos = [
            ('Placa Cuarcita Enigma (bloque)', 'PLACA-ENIGMA',
             'Pieza Cuarcita Enigma cortada', 'PIEZA-ENIGMA', 'cuarcita'),
            ('Placa Marmol Portoro (bloque)', 'PLACA-PORTORO',
             'Pieza Marmol Portoro cortada', 'PIEZA-PORTORO', 'marmol'),
        ]
        placas_ok = 0
        piezas_ok = 0
        for j, (nplaca, cplaca, npieza, cpieza, cat) in enumerate(ejemplos):
            try:
                placa = prod(cplaca)
                if not placa:
                    placa = Product.create({
                        'name': nplaca, 'default_code': cplaca, 'type': 'consu',
                        'is_storable': True, 'tracking': 'lot',
                        'categ_id': C(cat), 'uom_id': unidad.id,
                        'standard_price': 1800 + j * 400,
                    }).product_variant_id
                pieza = prod(cpieza)
                if not pieza:
                    pieza = Product.create({
                        'name': npieza, 'default_code': cpieza, 'type': 'consu',
                        'is_storable': True, 'tracking': 'lot',
                        'categ_id': C(cat), 'uom_id': unidad.id,
                        'list_price': 600 + j * 150, 'standard_price': 300 + j * 80,
                        'taxes_id': [(6, 0, sale_tax.ids)] if sale_tax else False,
                    }).product_variant_id
                # BoM: 1 placa -> 6 piezas
                bom = BoM.search([('product_tmpl_id', '=', pieza.product_tmpl_id.id)], limit=1)
                if not bom:
                    bom = BoM.create({
                        'product_tmpl_id': pieza.product_tmpl_id.id,
                        'product_qty': 6, 'type': 'normal',
                        'bom_line_ids': [(0, 0, {'product_id': placa.id, 'product_qty': 1})],
                    })
                # Stock de la placa madre con su lote
                lote_placa = Lot.search([('name', '=', 'PL-%s' % cplaca)], limit=1)
                if not lote_placa:
                    lote_placa = Lot.create({'name': 'PL-%s' % cplaca,
                                             'product_id': placa.id})
                    Quant._update_available_quantity(placa, ubic, 1, lot_id=lote_placa)
                    placas_ok += 1
                # Orden de fabricacion: cortar la placa en 6 piezas
                if not MO.search([('origin', '=', 'CORTE-%s' % cplaca)], limit=1):
                    mo = MO.create({
                        'product_id': pieza.id, 'product_qty': 6,
                        'bom_id': bom.id, 'origin': 'CORTE-%s' % cplaca,
                    })
                    mo.action_confirm()
                    mo.action_assign()
                    mo.qty_producing = 6
                    lote_pieza = (Lot.search([('name', '=', 'PZ-%s' % cpieza)], limit=1)
                                  or Lot.create({'name': 'PZ-%s' % cpieza,
                                                 'product_id': pieza.id}))
                    mo.lot_producing_ids = [(6, 0, [lote_pieza.id])]
                    # Consumo de la PLACA MADRE con su lote (genealogia padre->hijo)
                    for mv in mo.move_raw_ids:
                        mv.move_line_ids.unlink()
                        mv.move_line_ids = [(0, 0, {
                            'product_id': mv.product_id.id,
                            'lot_id': lote_placa.id if mv.product_id.id == placa.id else False,
                            'quantity': mv.product_uom_qty or 1,
                            'location_id': mv.location_id.id,
                            'location_dest_id': mv.location_dest_id.id,
                        })]
                        mv.picked = True
                    res = mo.button_mark_done()
                    if isinstance(res, dict) and res.get('res_model'):
                        wiz = env[res['res_model']].with_context(
                            res.get('context', {})).create({})
                        for meth in ('action_confirm', 'process',
                                     'action_backorder', 'action_done'):
                            if hasattr(wiz, meth):
                                getattr(wiz, meth)()
                                break
                    piezas_ok += 6
            except Exception as e:
                _logger.warning('Trazabilidad %s: %s', cplaca, e)
        print('Trazabilidad: placas', placas_ok, '| piezas producidas', piezas_ok)
    env.cr.commit()

    # --- 13) Acceso del Administrador a toda la operacion del ERP ---
    # El usuario Administrador debe poder revisar y operar los flujos creados
    # para Contabilidad sin depender de un perfil adicional.
    admin = env.ref('base.user_admin', raise_if_not_found=False)
    grupos_admin = grp(
        'sales_team.group_sale_manager',
        'stock.group_stock_manager',
        'purchase.group_purchase_manager',
            'account.group_account_user',
            'account.group_account_manager',
            'analytic.group_analytic_accounting',
    )
    if admin and grupos_admin:
        admin.write({'group_ids': [(4, group_id) for group_id in grupos_admin]})
        print('Administrador habilitado para Ventas, Compras, Inventario y Contabilidad.')

    # --- 14) Demostracion de tesoreria, presupuestos y control tributario ---
    # Cada registro usa nombres o referencias DEMO unicos, de modo que el seed
    # se pueda ejecutar en local y Render sin duplicar movimientos.
    Acc = env['account.account']
    Journal = env['account.journal']
    Caja = env['pierinelli.caja.chica']
    CajaMovimiento = env['pierinelli.caja.chica.movimiento']
    Tributo = env['pierinelli.control.tributario']
    Presupuesto = env['pierinelli.presupuesto.financiero']
    AM = env['account.move']
    hoy_demo = datetime.now().date()
    inicio_mes_demo = hoy_demo.replace(day=1)

    def cuenta_demo(code, name=None, account_type=None):
        account = Acc.search([('code', '=', code)], limit=1)
        if not account and name and account_type:
            account = Acc.create({
                'code': code, 'name': name, 'account_type': account_type,
                'company_ids': [(4, company.id)],
            })
        return account

    cuenta_caja = cuenta_demo('1020000') or cuenta_demo('1010000')
    cuenta_banco = cuenta_demo('1041001') or cuenta_demo('1041000')
    cuenta_movilidad = cuenta_demo('6311200')
    cuenta_suministros = cuenta_demo('6560000')
    cuenta_consultoria = cuenta_demo('6321000')
    cuenta_por_pagar = cuenta_demo('4211000')
    # PCGE: 4211 corresponde a comprobantes por recibir (no emitidas) y
    # 4212 a comprobantes emitidos. Algunas instalaciones antiguas del plan
    # local conservaban la denominacion de 4211 en ambas subcuentas.
    cuenta_emitidas = cuenta_demo('4212000')
    if cuenta_emitidas:
        cuenta_emitidas.name = 'Facturas, boletas y otros comprobantes por pagar - Emitidas'
    cuenta_depreciacion = cuenta_demo('6811100')
    cuenta_depreciacion_acum = cuenta_demo('3911100')
    cuenta_faltante = cuenta_demo(
        '6599900', 'Diferencias de caja - Faltantes', 'expense')
    cuenta_sobrante = cuenta_demo(
        '7599900', 'Diferencias de caja - Sobrantes', 'income_other')
    diario_banco = Journal.search([
        ('type', '=', 'bank'), ('default_account_id', '!=', False)], limit=1)
    diario_general = Journal.search([('type', '=', 'general')], limit=1)
    diario_caja = Journal.search([('code', '=', 'CCH')], limit=1)
    if not diario_caja and cuenta_caja:
        diario_caja = Journal.create({
            'name': 'Caja Chica Demo', 'code': 'CCH', 'type': 'cash',
            'company_id': company.id, 'default_account_id': cuenta_caja.id,
        })

    responsable_caja = Users.search([('login', '=', 'contabilidad')], limit=1) or admin
    proveedor_demo = proveedores[0] if proveedores else Partner.search(
        [('supplier_rank', '>', 0)], limit=1)
    cajas_demo = 0
    if all((diario_caja, diario_banco, cuenta_faltante, cuenta_sobrante,
            cuenta_movilidad, cuenta_suministros)):
        caja_cerrada = Caja.search([('name', '=', 'Caja Chica Demo - Cerrada')], limit=1)
        if not caja_cerrada:
            caja_cerrada = Caja.create({
                'name': 'Caja Chica Demo - Cerrada',
                'responsable_id': responsable_caja.id,
                'journal_id': diario_caja.id,
                'journal_reposicion_id': diario_banco.id,
                'cuenta_faltante_id': cuenta_faltante.id,
                'cuenta_sobrante_id': cuenta_sobrante.id,
                'currency_id': company.currency_id.id,
                'fondo_fijo': 2000.0,
                'fecha_apertura': inicio_mes_demo,
            })
            caja_cerrada.action_abrir()
            movimientos = [
                (cuenta_movilidad, 185.0, 'MOV-DEMO-001', 'Planilla de movilidad comercial'),
                (cuenta_suministros, 240.0, 'B001-458', 'Suministros de oficina'),
                (cuenta_movilidad, 60.0, 'B001-461', 'Traslado de muestras a obra'),
            ]
            for cuenta, importe, documento, descripcion in movimientos:
                movimiento = CajaMovimiento.create({
                    'caja_id': caja_cerrada.id, 'fecha': inicio_mes_demo,
                    'partner_id': proveedor_demo.id if proveedor_demo else False,
                    'cuenta_gasto_id': cuenta.id, 'importe': importe,
                    'documento': documento, 'descripcion': descripcion,
                })
                movimiento.action_contabilizar()
            caja_cerrada.action_reponer()
            # Se simula un faltante aprobado de S/ 10 para mostrar el ajuste.
            caja_cerrada.write({
                'arqueo_real': 1990.0, 'arqueo_confirmado': True,
            })
            caja_cerrada.action_ajustar_arqueo()
            caja_cerrada.action_cerrar()
            cajas_demo += 1

        caja_abierta = Caja.search([('name', '=', 'Caja Chica Demo - Abierta')], limit=1)
        if not caja_abierta:
            caja_abierta = Caja.create({
                'name': 'Caja Chica Demo - Abierta',
                'responsable_id': responsable_caja.id,
                'journal_id': diario_caja.id,
                'journal_reposicion_id': diario_banco.id,
                'cuenta_faltante_id': cuenta_faltante.id,
                'cuenta_sobrante_id': cuenta_sobrante.id,
                'currency_id': company.currency_id.id,
                'fondo_fijo': 1500.0,
                'fecha_apertura': hoy_demo,
            })
            caja_abierta.action_abrir()
            for cuenta, importe, documento, descripcion in [
                (cuenta_movilidad, 95.0, 'MOV-DEMO-002', 'Movilidad de visita a cliente'),
                (cuenta_suministros, 130.0, 'F001-087', 'Materiales de embalaje'),
            ]:
                movimiento = CajaMovimiento.create({
                    'caja_id': caja_abierta.id, 'fecha': hoy_demo,
                    'partner_id': proveedor_demo.id if proveedor_demo else False,
                    'cuenta_gasto_id': cuenta.id, 'importe': importe,
                    'documento': documento, 'descripcion': descripcion,
                })
                movimiento.action_contabilizar()
            cajas_demo += 1
    print('Cajas chicas de demostracion creadas:', cajas_demo)

    def asiento_demo(ref, fecha, tipo, lineas):
        move = AM.search([('ref', '=', ref)], limit=1)
        if not move and diario_general:
            move = AM.create({
                'move_type': 'entry', 'journal_id': diario_general.id,
                'date': fecha, 'ref': ref, 'tipo_operacion_contable': tipo,
                'line_ids': [(0, 0, values) for values in lineas],
            })
            move.action_post()
        return move

    if all((cuenta_consultoria, cuenta_por_pagar)):
        asiento_demo('DEMO-PROVISION-AGOSTO', inicio_mes_demo, 'provision', [
            {'account_id': cuenta_consultoria.id, 'name': 'Provision servicio contable', 'debit': 3500.0},
            {'account_id': cuenta_por_pagar.id, 'name': 'Provision servicio contable', 'credit': 3500.0},
        ])
    if all((cuenta_depreciacion, cuenta_depreciacion_acum)):
        asiento_demo('DEMO-DEPRECIACION-AGOSTO', inicio_mes_demo, 'depreciacion', [
            {'account_id': cuenta_depreciacion.id, 'name': 'Depreciacion mensual demostrativa', 'debit': 1250.0},
            {'account_id': cuenta_depreciacion_acum.id, 'name': 'Depreciacion mensual demostrativa', 'credit': 1250.0},
        ])
    if all((cuenta_suministros, cuenta_por_pagar)) and not AM.search([('ref', '=', 'DEMO-ASIENTO-BORRADOR')], limit=1):
        AM.create({
            'move_type': 'entry', 'journal_id': diario_general.id,
            'date': hoy_demo, 'ref': 'DEMO-ASIENTO-BORRADOR',
            'tipo_operacion_contable': 'ajuste',
            'line_ids': [
                (0, 0, {'account_id': cuenta_suministros.id, 'name': 'Ajuste pendiente de aprobar', 'debit': 420.0}),
                (0, 0, {'account_id': cuenta_por_pagar.id, 'name': 'Ajuste pendiente de aprobar', 'credit': 420.0}),
            ],
        })

    factura_cliente_demo = AM.search([
        ('move_type', '=', 'out_invoice'), ('state', '=', 'posted')],
        order='invoice_date desc, id desc', limit=1)
    factura_proveedor_demo = AM.search([
        ('move_type', '=', 'in_invoice'), ('state', '=', 'posted')],
        order='invoice_date desc, id desc', limit=1)
    if factura_cliente_demo:
        factura_cliente_demo.numero_externo = factura_cliente_demo.numero_externo or 'FEXT-DEMO-001'
        if not Tributo.search([('notas', '=', 'DEMO-DETRACCION-001')], limit=1):
            Tributo.create({
                'move_id': factura_cliente_demo.id, 'tipo': 'detraccion',
                'porcentaje': 4.0, 'base': 5000.0, 'fecha': hoy_demo,
                'constancia': 'CONST-DEMO-DET-001', 'estado': 'pendiente',
                'notas': 'DEMO-DETRACCION-001',
            })
    if factura_proveedor_demo:
        factura_proveedor_demo.numero_externo = factura_proveedor_demo.numero_externo or 'FEXT-DEMO-002'
        if not Tributo.search([('notas', '=', 'DEMO-RETENCION-001')], limit=1):
            Tributo.create({
                'move_id': factura_proveedor_demo.id, 'tipo': 'retencion',
                'porcentaje': 3.0, 'base': 3200.0, 'fecha': hoy_demo,
                'constancia': 'RET-DEMO-001', 'estado': 'pagado',
                'notas': 'DEMO-RETENCION-001',
            })

    referidor_demo = Partner.search([('name', '=', 'Arquitecta Referidora Demo')], limit=1)
    if not referidor_demo:
        referidor_demo = Partner.create({
            'name': 'Arquitecta Referidora Demo', 'email': 'referidos@demo.pe',
            'customer_rank': 1,
        })
    for cliente in clientes[:3]:
        if not cliente.referidor_id:
            cliente.referidor_id = referidor_demo.id

    lineas_presupuesto = []
    for cuenta, importe in (
            (cuenta_movilidad, 5000.0), (cuenta_suministros, 6000.0),
            (cuenta_consultoria, 9000.0), (cuenta_depreciacion, 2500.0)):
        if cuenta:
            lineas_presupuesto.append((0, 0, {
                'cuenta_id': cuenta.id, 'presupuestado': importe,
            }))
    if lineas_presupuesto and not Presupuesto.search([
            ('name', '=', 'Presupuesto Operativo - DEMO')], limit=1):
        presupuesto = Presupuesto.create({
            'name': 'Presupuesto Operativo - DEMO',
            'fecha_inicio': inicio_mes_demo,
            'fecha_fin': hoy_demo.replace(day=28),
            'linea_ids': lineas_presupuesto,
        })
        presupuesto.action_aprobar()

    # --- 15) Casos demostrativos para libros 7.1 y 8.2 ---
    # Permiten que el Centro de Libros muestre contenido aun cuando la empresa
    # todavia no haya registrado activos ni compras a no domiciliados reales.
    diario_compras = Journal.search([
        ('type', '=', 'purchase'), ('company_id', '=', company.id)], limit=1)
    cuenta_activo = cuenta_demo(
        '3361000', 'Equipo para procesamiento de piedra - Demo', 'asset_fixed')
    cuenta_importacion = (
        cuenta_demo('6091000')
        or cuenta_demo('6011000')
        or cuenta_demo('6311000')
        or cuenta_demo('6099000', 'Compras de importación - Demo', 'expense_direct_cost'))

    try:
        if diario_compras and cuenta_activo and not AM.search([
                ('ref', '=', 'DEMO-7.1-ACTIVO')], limit=1):
            activo_bill = AM.create({
                'move_type': 'in_invoice',
                'journal_id': diario_compras.id,
                'partner_id': proveedor_demo.id,
                'invoice_date': hoy_demo,
                'ref': 'DEMO-7.1-ACTIVO',
                'invoice_line_ids': [(0, 0, {
                    'name': 'Pulidora industrial de cantos - Activo Demo',
                    'account_id': cuenta_activo.id,
                    'quantity': 1.0,
                    'price_unit': 4800.0,
                    'tax_ids': [(6, 0, purchase_tax.ids)] if purchase_tax else False,
                })],
            })
            if factura and 'l10n_latam_document_type_id' in activo_bill._fields:
                activo_bill.l10n_latam_document_type_id = factura.id
            if 'l10n_latam_document_number' in activo_bill._fields:
                activo_bill.l10n_latam_document_number = 'F009-00000471'
            activo_bill.action_post()

        proveedor_exterior = Partner.search([
            ('name', '=', 'Marmol Design Italia SRL - Demo')], limit=1)
        if not proveedor_exterior:
            proveedor_exterior = Partner.create({
                'name': 'Marmol Design Italia SRL - Demo',
                'is_company': True,
                'supplier_rank': 1,
                'country_id': env.ref('base.it').id,
                'l10n_latam_identification_type_id': env.ref('l10n_pe.it_NDTD').id,
                'vat': 'IT-DEMO-10458963',
                'email': 'exportaciones@proveedor-demo.invalid',
            })
        usd = env.ref('base.USD', raise_if_not_found=False)
        comprobante_91 = env.ref('l10n_pe.document_type91', raise_if_not_found=False)
        if diario_compras and cuenta_importacion and not AM.search([
                ('ref', '=', 'DEMO-8.2-NO-DOMICILIADO')], limit=1):
            exterior_bill = AM.create({
                'move_type': 'in_invoice',
                'journal_id': diario_compras.id,
                'partner_id': proveedor_exterior.id,
                'invoice_date': hoy_demo,
                'currency_id': usd.id if usd else company.currency_id.id,
                'ref': 'DEMO-8.2-NO-DOMICILIADO',
                'invoice_line_ids': [(0, 0, {
                    'name': 'Lote de mármol importado - muestra 8.2',
                    'account_id': cuenta_importacion.id,
                    'quantity': 12.5,
                    'price_unit': 320.0,
                    'tax_ids': [(5, 0, 0)],
                })],
            })
            if comprobante_91 and 'l10n_latam_document_type_id' in exterior_bill._fields:
                exterior_bill.l10n_latam_document_type_id = comprobante_91.id
            if 'l10n_latam_document_number' in exterior_bill._fields:
                exterior_bill.l10n_latam_document_number = 'INV-IT-2026-0184'
            exterior_bill.action_post()
        print('Casos de libros 7.1 y 8.2 verificados.')
    except Exception as e:
        _logger.warning('Casos demostrativos 7.1/8.2: %s', e)

    print('Datos contables de demostracion verificados.')
    env.cr.commit()

    ICP.set_param('pierinelli.seed_pe_version', SEED_VERSION)
    env.cr.commit()
    print('SEED COMPLETO (version %s).' % SEED_VERSION)
