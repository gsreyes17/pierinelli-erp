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
SEED_VERSION = '6'
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
    print('Productos catalogo:', creados_prod, '| con imagen:', con_imagen,
          '| total JSON:', len(catalogo))

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
                'product_uom_qty': 5 + ((i + k * 3) % 25),
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
        # Entregar la mayoria
        if i % 4 != 0:
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

    ICP.set_param('pierinelli.seed_pe_version', SEED_VERSION)
    env.cr.commit()
    print('SEED COMPLETO (version %s).' % SEED_VERSION)
