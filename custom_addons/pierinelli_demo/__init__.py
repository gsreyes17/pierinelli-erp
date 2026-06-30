# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

LANG = 'es_419'


def _deliver(order, env):
    for picking in order.picking_ids:
        if picking.state in ('done', 'cancel'):
            continue
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
        picking.move_ids.picked = True
        try:
            picking._action_done()
        except Exception:
            pass


def _load_demo(env):
    """Crea la demo completa (idempotente): idioma, clientes, ventas y CRM."""
    Partner = env['res.partner']
    SO = env['sale.order']
    Lead = env['crm.lead']
    pe = env.ref('base.pe')
    wh = env.ref('stock.warehouse0')

    # --- Idioma espanol por defecto ---
    lang = env['res.lang'].with_context(active_test=False).search(
        [('code', '=', LANG)], limit=1)
    if lang and not lang.active:
        lang.active = True
    admin = env.ref('base.user_admin', raise_if_not_found=False)
    if admin:
        admin.lang = LANG
    env.ref('base.main_company').partner_id.lang = LANG
    env['ir.default'].set('res.partner', 'lang', LANG)

    def prod(code):
        return env['product.product'].search([('default_code', '=', code)], limit=1)

    def get_partner(name, **vals):
        p = Partner.search([('name', '=', name)], limit=1)
        if not p:
            vals.update({'name': name, 'is_company': True, 'lang': LANG,
                         'country_id': pe.id})
            p = Partner.create(vals)
        return p

    # --- Clientes / estudios ---
    clientes = [
        ('Constructora Andina Demo S.A.C.', 'compras@constructora-andina-demo.pe', 'Av. Javier Prado Este 4200, Surco - Lima'),
        ('Estudio Arquitectura Vela & Asociados', 'contacto@vela-arq.pe', 'Av. El Sol 250, San Isidro - Lima'),
        ('Inmobiliaria Costa Verde S.A.C.', 'proyectos@costaverde.pe', 'Malecon Cisneros 1450, Miraflores - Lima'),
        ('Disenos Interiores Lumen E.I.R.L.', 'hola@lumen-interiores.pe', 'Calle Berlin 480, Miraflores - Lima'),
        ('Constructora del Pacifico S.A.', 'compras@delpacifico.pe', 'Av. Industrial 2100, Arequipa'),
        ('Arq. Mariana Foppiani - Estudio', 'mariana@foppiani.studio', 'Jr. Colon 320, Trujillo'),
    ]
    P = [get_partner(n, email=e, street=s) for n, e, s in clientes]

    # --- Pedido principal de demostracion (confirmado + entregado) ---
    ventas = [
        (P[0], [('MAR-PORTORO', 15), ('CUA-ENIGMA', 22), ('ONX-ORO', 8)], 5, True),
        (P[1], [('MAR-PORTORO', 12), ('CRZ-CALACATTA', 6)], 40, True),
        (P[2], [('CUA-ENIGMA', 30), ('GRA-MAORI', 18)], 28, True),
        (P[3], [('CRZ-CALACATTA', 9)], 21, False),
        (P[4], [('SIN-AMAZONICO', 25), ('GRA-MAORI', 12)], 14, True),
        (P[5], [('ONX-ORO', 5), ('MAR-PORTORO', 8)], 7, False),
        (P[2], [('CUA-ENIGMA', 16)], 3, True),
    ]
    for partner, lineas, dias, entregar in ventas:
        tag = 'DEMO-%s-%s' % (partner.id, dias)
        if SO.search([('client_order_ref', '=', tag)], limit=1):
            continue
        order = SO.create({
            'partner_id': partner.id,
            'warehouse_id': wh.id,
            'client_order_ref': tag,
            'date_order': datetime.now() - timedelta(days=dias),
            'order_line': [(0, 0, {'product_id': prod(c).id, 'product_uom_qty': q})
                           for c, q in lineas],
        })
        order.action_confirm()
        if entregar:
            _deliver(order, env)

    # --- CRM: oportunidades (embudo) ---
    stages = {
        'new': env.ref('crm.stage_lead1'),
        'qualified': env.ref('crm.stage_lead2'),
        'proposition': env.ref('crm.stage_lead3'),
        'won': env.ref('crm.stage_lead4'),
    }
    oportunidades = [
        ('Encimeras Marmol Portoro - Penthouse Miraflores', P[1], 22500, 'proposition'),
        ('Revestimiento fachada cuarcita - Torre Costa Verde', P[2], 68000, 'qualified'),
        ('Isla cocina Silestone - Depto modelo Lumen', P[3], 9800, 'new'),
        ('Pisos porcelanico gran formato - Obra Arequipa', P[4], 41000, 'proposition'),
        ('Bano principal onix retroiluminado - Casa Foppiani', P[5], 15600, 'won'),
    ]
    for name, partner, revenue, stage in oportunidades:
        if not Lead.search([('name', '=', name)], limit=1):
            Lead.create({
                'name': name,
                'type': 'opportunity',
                'partner_id': partner.id,
                'expected_revenue': revenue,
                'stage_id': stages[stage].id,
                'email_from': partner.email,
            })
