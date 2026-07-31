# -*- coding: utf-8 -*-
"""
La plancha como entidad (Plan Inventario V2, Fase 2).

Cada plancha fisica es un lote (stock.lot) de su producto. El producto sigue
siendo el tipo de piedra (catalogo, precio, costo promedio); el lote es la
plancha concreta (codigo interno, medidas, foto, ubicacion, condicion, reserva).
"""
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

# Dimension minima (en metros) bajo la cual un retorno de corte se considera
# retazo y el sistema sugiere mandarlo a merma o liquidacion (Plan V2 §7.1).
RETAZO_MIN_M = 0.5

# Dias que dura una reserva comercial (regla de negocio del cliente).
DIAS_RESERVA = 7

# Dias en almacen a partir de los cuales una plancha pasa a condicion "Hueso".
DIAS_HUESO = 365


class StockLot(models.Model):
    _name = 'stock.lot'
    _inherit = ['stock.lot', 'image.mixin']

    # ------------------------------------------------------------------
    #  Medidas
    # ------------------------------------------------------------------
    largo = fields.Float('Largo (m)', digits=(6, 2), tracking=True)
    alto = fields.Float('Alto (m)', digits=(6, 2), tracking=True)
    espesor = fields.Float('Espesor (cm)', digits=(4, 1))
    m2_bruto = fields.Float(
        'M. bruto (m²)', compute='_compute_m2_bruto', store=True,
        digits=(8, 2), help='Largo x alto de la plancha completa.')
    m2_neto = fields.Float(
        'M. neto (m²)', digits=(8, 2),
        help='Metros cuadrados vendibles (descontando defectos de borde). '
             'Es la cantidad que entra a stock.')
    m2_disponible = fields.Float(
        'Stock (m²)', compute='_compute_m2_disponible', store=True,
        digits=(8, 2),
        help='Existencia fisica actual de la plancha (suma de sus quants '
             'en ubicaciones internas). Almacenado para poder ordenar y '
             'agrupar en listados grandes.')

    # ------------------------------------------------------------------
    #  Clasificacion y situacion
    # ------------------------------------------------------------------
    condicion = fields.Selection(
        [('estandar', 'Estandar'),
         ('oferta', 'Oferta'),
         ('liquidacion', 'Liquidacion'),
         ('hueso', 'Hueso')],
        string='Condicion', default='estandar', tracking=True, index=True,
        help='Hueso: mas de un anio en almacen, pendiente de pasar a oferta '
             'o liquidacion. El sistema lo marca automaticamente.')
    estado = fields.Selection(
        [('disponible', 'Disponible'),
         ('reservada', 'Reservada'),
         ('vendida', 'Vendida')],
        string='Estado', compute='_compute_estado', store=True, index=True)
    tipo_material = fields.Selection(
        related='product_id.tipo_material', store=True, string='Tipo material')
    ubicacion_ref = fields.Char(
        'Ubicacion referencial',
        help='Zona/rack donde buscar la plancha (ej. "Zona A · Rack 3"). '
             'Texto libre, no mueve stock.')
    observaciones = fields.Text(
        'Observaciones',
        help='Condicion fisica: quinie, despunte, rayadura, veta especial...')
    ref_importacion = fields.Char('Ref. importacion')
    fecha_ingreso = fields.Date(
        'F. ingreso', default=fields.Date.context_today, index=True)
    antiguedad_dias = fields.Integer(
        'Antiguedad (dias)', compute='_compute_antiguedad')
    plancha_madre_id = fields.Many2one(
        'stock.lot', string='Plancha madre', index=True,
        help='Si esta plancha es el retorno de un corte, de que plancha '
             'proviene.')
    plancha_hija_ids = fields.One2many(
        'stock.lot', 'plancha_madre_id', string='Retornos de corte')

    # ------------------------------------------------------------------
    #  Reserva comercial y venta
    # ------------------------------------------------------------------
    cliente_reserva_id = fields.Many2one(
        'res.partner', string='Cliente', tracking=True)
    asesor_id = fields.Many2one(
        'res.users', string='Asesor', tracking=True,
        help='Vendedor que realizo la ultima accion (reserva o venta).')
    reserva_inicio = fields.Date('Ini. reserva')
    reserva_fin = fields.Date('Fin reserva')
    comprobante = fields.Char('Nro. comprobante', tracking=True)
    fecha_comprobante = fields.Date('F. comprobante')

    # Costo (solo visible para inventario/gerencia, no para comercial)
    costo_kardex = fields.Float(
        related='product_id.standard_price', string='Costo kardex (S//m²)',
        groups='stock.group_stock_user')

    # ------------------------------------------------------------------
    #  Computes
    # ------------------------------------------------------------------
    @api.depends('largo', 'alto')
    def _compute_m2_bruto(self):
        for lot in self:
            lot.m2_bruto = round((lot.largo or 0.0) * (lot.alto or 0.0), 2)

    @api.onchange('largo', 'alto')
    def _onchange_dimensiones(self):
        """El neto parte igual al bruto; se ajusta a mano si hay defectos."""
        if not self.m2_neto:
            self.m2_neto = round((self.largo or 0.0) * (self.alto or 0.0), 2)

    @api.depends('quant_ids.quantity', 'quant_ids.location_id')
    def _compute_m2_disponible(self):
        for lot in self:
            lot.m2_disponible = sum(
                q.quantity for q in lot.quant_ids
                if q.location_id.usage == 'internal')

    @api.depends('m2_disponible', 'cliente_reserva_id', 'reserva_fin')
    def _compute_estado(self):
        hoy = fields.Date.context_today(self)
        for lot in self:
            reserva_vigente = lot.cliente_reserva_id and (
                not lot.reserva_fin or lot.reserva_fin >= hoy)
            if lot.m2_disponible <= 0:
                lot.estado = 'vendida'
            elif reserva_vigente:
                lot.estado = 'reservada'
            else:
                lot.estado = 'disponible'

    def _compute_antiguedad(self):
        hoy = fields.Date.context_today(self)
        for lot in self:
            lot.antiguedad_dias = (
                (hoy - lot.fecha_ingreso).days if lot.fecha_ingreso else 0)

    # ------------------------------------------------------------------
    #  Codigo interno: PREFIJO + MMAA + . + correlativo
    # ------------------------------------------------------------------
    @api.model
    def siguiente_codigo(self, product, count=1, fecha=None):
        """Genera los siguientes codigos internos para un producto.

        Ej.: Cuarcita Iron Green, octubre 2025, count=3 ->
             ['CIG1025.01', 'CIG1025.02', 'CIG1025.03']
        Los retornos de corte (CIG1025.01.01) no cuentan como correlativo
        nuevo: extienden el codigo de su plancha madre.
        """
        fecha = fecha or fields.Date.context_today(self)
        prefijo = product.product_tmpl_id.prefijo_plancha or 'PLN'
        base = '%s%s.' % (prefijo, fecha.strftime('%m%y'))
        existentes = self.search([
            ('product_id', '=', product.id),
            ('name', '=like', base + '%'),
        ])
        numeros = []
        for lot in existentes:
            primero = lot.name[len(base):].split('.')[0]
            if primero.isdigit():
                numeros.append(int(primero))
        inicio = max(numeros, default=0) + 1
        return ['%s%02d' % (base, inicio + i) for i in range(count)]

    def siguiente_codigo_corte(self):
        """Codigo del retorno de corte de esta plancha: NAME.01, NAME.02..."""
        self.ensure_one()
        vueltas = self.search_count([('plancha_madre_id', '=', self.id)])
        return '%s.%02d' % (self.name, vueltas + 1)

    # ------------------------------------------------------------------
    #  Reserva comercial (7 dias)
    # ------------------------------------------------------------------
    def action_reservar(self):
        hoy = fields.Date.context_today(self)
        for lot in self:
            if not lot.cliente_reserva_id:
                raise UserError(_(
                    'Asigna primero el cliente en la ficha de la plancha '
                    '%s y vuelve a pulsar Reservar.') % lot.name)
            if lot.estado == 'vendida':
                raise UserError(_(
                    'La plancha %s ya no tiene stock disponible.') % lot.name)
            lot.write({
                'reserva_inicio': hoy,
                'reserva_fin': hoy + timedelta(days=DIAS_RESERVA),
                'asesor_id': self.env.user.id,
            })
            lot.message_post(body=_(
                'Reservada para %(cliente)s por %(asesor)s hasta el %(fin)s.',
                cliente=lot.cliente_reserva_id.display_name,
                asesor=self.env.user.name,
                fin=lot.reserva_fin))

    def action_liberar(self):
        for lot in self:
            lot.message_post(body=_(
                'Reserva liberada (cliente: %s).',
                lot.cliente_reserva_id.display_name or '-'))
            lot.write({
                'cliente_reserva_id': False,
                'reserva_inicio': False,
                'reserva_fin': False,
            })

    # ------------------------------------------------------------------
    #  Alertas al crear (retazo pequenio - Plan V2 §7.1)
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        lots = super().create(vals_list)
        for lot in lots:
            dims = [d for d in (lot.largo, lot.alto) if d]
            if lot.plancha_madre_id and dims and min(dims) < RETAZO_MIN_M:
                lot.message_post(body=_(
                    'Retazo pequenio: una dimension quedo por debajo de '
                    '%(min).2f m tras el corte. Considerar pasarlo a merma '
                    'o liquidacion en lugar de stock vendible.',
                    min=RETAZO_MIN_M))
        return lots

    # ------------------------------------------------------------------
    #  Tareas automaticas (crons)
    # ------------------------------------------------------------------
    @api.model
    def _cron_marcar_hueso(self):
        """Planchas con mas de un anio en almacen pasan a condicion Hueso."""
        limite = fields.Date.today() - timedelta(days=DIAS_HUESO)
        planchas = self.search([
            ('condicion', '=', 'estandar'),
            ('fecha_ingreso', '<', limite),
            ('m2_disponible', '>', 0),
        ])
        planchas.write({'condicion': 'hueso'})
        for lot in planchas:
            lot.message_post(body=_(
                'Mas de %s dias en almacen: pasa a condicion Hueso. '
                'Pendiente de gestion (oferta o liquidacion).') % DIAS_HUESO)
        return True

    @api.model
    def _cron_liberar_reservas(self):
        """Libera las reservas comerciales vencidas (regla de los 7 dias)."""
        hoy = fields.Date.today()
        vencidas = self.search([
            ('cliente_reserva_id', '!=', False),
            ('reserva_fin', '<', hoy),
            ('comprobante', '=', False),   # si ya se facturo, no se libera
        ])
        for lot in vencidas:
            lot.message_post(body=_(
                'Reserva vencida el %(fin)s (cliente: %(cliente)s): '
                'la plancha vuelve a estar disponible.',
                fin=lot.reserva_fin,
                cliente=lot.cliente_reserva_id.display_name))
        vencidas.write({
            'cliente_reserva_id': False,
            'reserva_inicio': False,
            'reserva_fin': False,
        })
        return True
