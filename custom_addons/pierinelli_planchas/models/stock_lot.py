# -*- coding: utf-8 -*-
"""
La plancha como entidad (Plan Inventario V2, Fase 2).

Cada plancha fisica es un lote (stock.lot) de su producto. El producto sigue
siendo el tipo de piedra (catalogo, precio, costo promedio); el lote es la
plancha concreta (codigo interno, medidas, foto, ubicacion, condicion, reserva).
"""
import math
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

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
    #  Formato de venta: a granel por m2, o en losas pre-cortadas
    # ------------------------------------------------------------------
    #  El stock SIEMPRE se mueve en m2 (ver decision 2 del Plan V2: el factor
    #  de conversion de UoM en Odoo es global, y cada plancha tiene distintos
    #  m2, asi que no puede existir una unidad "losa"). Las piezas son una capa
    #  de conteo y precio encima de los m2: no tocan quants, kardex ni AVCO.
    modo_venta = fields.Selection(
        [('m2', 'Por m² (a medida)'),
         ('piezas', 'Losas pre-cortadas')],
        string='Formato de venta', default='m2', required=True, index=True,
        tracking=True,
        help='Como se comercializa esta plancha. "Por m²": se corta a la '
             'medida que pida el cliente. "Losas pre-cortadas": se vende en '
             'piezas de un tamano fijo.')
    pieza_largo = fields.Float('Pieza: largo (m)', digits=(6, 2))
    pieza_alto = fields.Float('Pieza: alto (m)', digits=(6, 2))
    m2_por_pieza = fields.Float(
        'm² por pieza', compute='_compute_piezas', store=True, digits=(8, 4),
        help='Superficie de cada losa pre-cortada.')
    piezas_disponibles = fields.Integer(
        'Piezas disponibles', compute='_compute_piezas', store=True,
        help='Cuantas losas completas salen del stock actual. ALMACENADO a '
             'proposito: los campos calculados no se pueden usar en dominios '
             'SQL, y este se necesita para filtrar planchas al vender.')

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
    aptitud_comercial = fields.Selection(
        [('vendible', 'Vendible'), ('liquidacion', 'Liquidacion'),
         ('muestra', 'Muestra / no vendible'),
         ('pendiente', 'Pendiente de revision')],
        string='Aptitud comercial', default='vendible', required=True,
        tracking=True, index=True,
        help='Los retazos pequenos quedan pendientes hasta que Operaciones '
             'defina si se venden en liquidacion o se usan como muestra.')
    tipo_material = fields.Selection(
        related='product_id.tipo_material', store=True, string='Tipo material')
    tiene_foto_individual = fields.Boolean(
        'Foto individual', compute='_compute_tiene_foto_individual', store=True,
        help='Indica si la ficha tiene una foto propia de esta plancha. Es '
             'obligatoria para vender materiales naturales.')

    # --- Columnas de la tabla global del ERP anterior (Expectativas.md) ---
    # Espejos del producto/ubicacion para que la tabla de planchas muestre
    # TODAS las columnas que la empresa manejaba, sin ir ficha por ficha.
    codigo_sap = fields.Char(
        related='product_id.default_code', string='Codigo SAP')
    # NO es related a location_id.warehouse_id: el location_id del lote queda
    # vacio cuando el lote esta repartido en varias ubicaciones — exactamente
    # el caso de una plancha vendida en parte (quant en Customers + sobrante en
    # el almacen). Se calcula desde los quants INTERNOS, que es donde de verdad
    # esta el material restante.
    almacen_id = fields.Many2one(
        'stock.warehouse', string='Almacen',
        compute='_compute_almacen_id', store=True)
    subfamilia_id = fields.Many2one(
        related='product_id.categ_id', string='Subfamilia', store=True)
    familia_id = fields.Many2one(
        'product.category', related='product_id.categ_id.parent_id',
        string='Familia', store=True)
    precio_venta = fields.Float(
        related='product_id.list_price', string='Precio (S//m²)')
    codigo_barra = fields.Char(
        'Codigo de barras',
        help='Reservado para la futura integracion de etiquetas / lector de '
             'codigo de barras. Hoy se puede llenar a mano si se desea.')
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
    reserva_pedido_id = fields.Many2one(
        'sale.order', string='Pedido de reserva', readonly=True, copy=False)
    asesor_id = fields.Many2one(
        'res.users', string='Asesor', tracking=True,
        help='Vendedor que realizo la ultima accion (reserva o venta).')
    reserva_inicio = fields.Date('Ini. reserva')
    reserva_fin = fields.Date('Fin reserva')
    reserva_dias = fields.Integer(
        'Dias de reserva', default=DIAS_RESERVA,
        help='Entre 1 y 7 dias. La fecha fin se calcula automaticamente.')
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

    @api.depends('modo_venta', 'pieza_largo', 'pieza_alto', 'm2_disponible')
    def _compute_piezas(self):
        """m2 por losa y cuantas losas completas quedan en la plancha."""
        for lot in self:
            if lot.modo_venta != 'piezas':
                lot.m2_por_pieza = 0.0
                lot.piezas_disponibles = 0
                continue
            m2 = round((lot.pieza_largo or 0.0) * (lot.pieza_alto or 0.0), 4)
            lot.m2_por_pieza = m2
            # Solo piezas ENTERAS: si sobran 0.97 de losa, esa losa no existe,
            # asi que se trunca (floor), no se redondea. El epsilon evita que
            # un 15.999999 por error de coma flotante se quede en 15.
            lot.piezas_disponibles = (
                int(math.floor((lot.m2_disponible or 0.0) / m2 + 1e-6))
                if m2 > 0 else 0)

    @api.constrains('modo_venta', 'pieza_largo', 'pieza_alto', 'm2_neto')
    def _check_pieza(self):
        for lot in self:
            if lot.modo_venta != 'piezas':
                continue
            if lot.pieza_largo <= 0 or lot.pieza_alto <= 0:
                raise ValidationError(_(
                    'Plancha %s: en "Losas pre-cortadas" hay que indicar el '
                    'largo y el alto de la pieza.') % lot.name)
            if lot.m2_neto and lot.m2_por_pieza > lot.m2_neto:
                raise ValidationError(_(
                    'Plancha %(p)s: la pieza (%(pieza).2f m²) no cabe en la '
                    'plancha (%(total).2f m²).',
                    p=lot.name, pieza=lot.m2_por_pieza, total=lot.m2_neto))

    @api.depends('quant_ids.quantity', 'quant_ids.location_id')
    def _compute_almacen_id(self):
        """Almacen donde queda material fisico de la plancha (quants internos
        con stock). Si no queda nada (vendida entera), el ultimo almacen que
        la tuvo, para que la fila no pierda la referencia."""
        for lot in self:
            internos = lot.quant_ids.filtered(
                lambda q: q.location_id.usage == 'internal')
            con_stock = internos.filtered(lambda q: q.quantity > 0)
            quants = con_stock or internos
            lot.almacen_id = quants[:1].location_id.warehouse_id

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

    @api.depends('image_1920')
    def _compute_tiene_foto_individual(self):
        for lot in self:
            lot.tiene_foto_individual = bool(lot.image_1920)

    def action_ver_imagen_plancha(self):
        """Abre la imagen original fuera del formulario para inspeccionarla."""
        self.ensure_one()
        if not self.image_1920:
            raise UserError(_('La plancha %s todavia no tiene foto individual.') % self.name)
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/image/stock.lot/%s/image_1920?unique=%s' % (self.id, self.write_date),
            'target': 'new',
        }

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
            lot._check_disponible_comercial()
            dias = lot.reserva_dias or DIAS_RESERVA
            if not 1 <= dias <= DIAS_RESERVA:
                raise UserError(_(
                    'La reserva debe durar entre 1 y %s dias.') % DIAS_RESERVA)
            lot.write({
                'reserva_inicio': hoy,
                'reserva_fin': hoy + timedelta(days=dias),
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
                'reserva_pedido_id': False,
                'reserva_dias': DIAS_RESERVA,
                'asesor_id': False,
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
                lot.aptitud_comercial = 'pendiente'
                lot.message_post(body=_(
                    'Retazo pequenio: una dimension quedo por debajo de '
                    '%(min).2f m tras el corte. Considerar pasarlo a merma '
                    'o liquidacion en lugar de stock vendible.',
                    min=RETAZO_MIN_M))
        return lots

    def _check_disponible_comercial(self):
        """Una plancha natural requiere foto; un retazo pendiente no se ofrece."""
        for lot in self:
            if lot.tipo_material == 'natural' and not lot.image_1920:
                raise UserError(_(
                    'La plancha natural %s no puede reservarse ni venderse '
                    'sin su foto individual.') % lot.name)
            if lot.aptitud_comercial not in ('vendible', 'liquidacion'):
                raise UserError(_(
                    'La plancha %s no esta disponible comercialmente. '
                    'Operaciones debe definir primero el destino del retazo.') % lot.name)

    def write(self, vals):
        """Completa las fechas antes de que corran las restricciones.

        En listas editables Odoo guarda una celda por vez; el onchange del
        navegador no siempre llega antes del constraint. Este refuerzo hace que
        cambiar cliente, inicio o dias sea una unica reserva consistente.
        """
        reservation_fields = {'cliente_reserva_id', 'reserva_inicio', 'reserva_dias'}
        if not reservation_fields.intersection(vals):
            return super().write(vals)
        result = True
        for lot in self:
            values = dict(vals)
            cliente_id = values.get('cliente_reserva_id', lot.cliente_reserva_id.id)
            if cliente_id:
                inicio = fields.Date.to_date(
                    values.get('reserva_inicio') or lot.reserva_inicio
                    or fields.Date.context_today(lot))
                dias = values['reserva_dias'] if 'reserva_dias' in values \
                    else (lot.reserva_dias or DIAS_RESERVA)
                # La fecha final siempre depende del inicio y del plazo; no se
                # acepta una fecha digitada manualmente que rompa la regla.
                values['reserva_inicio'] = inicio
                values['reserva_fin'] = inicio + timedelta(days=dias)
            result = super(StockLot, lot).write(values) and result
        return result

    @api.onchange('cliente_reserva_id', 'reserva_inicio', 'reserva_dias')
    def _onchange_reserva_fechas(self):
        """La fecha final no se digita: deriva del plazo permitido."""
        for lot in self:
            if lot.cliente_reserva_id:
                lot.reserva_inicio = lot.reserva_inicio or fields.Date.context_today(lot)
                dias = min(max(lot.reserva_dias or DIAS_RESERVA, 1), DIAS_RESERVA)
                lot.reserva_dias = dias
                lot.reserva_fin = lot.reserva_inicio + timedelta(days=dias)

    @api.constrains('cliente_reserva_id', 'reserva_inicio', 'reserva_fin', 'reserva_dias')
    def _check_reserva_duracion(self):
        for lot in self:
            if not lot.cliente_reserva_id:
                continue
            if not lot.reserva_inicio or not lot.reserva_fin:
                raise ValidationError(_('Toda reserva debe tener fecha de inicio y fin.'))
            if not 1 <= lot.reserva_dias <= DIAS_RESERVA:
                raise ValidationError(_(
                    'La reserva de %s debe durar entre 1 y %s dias.')
                    % (lot.name, DIAS_RESERVA))
            if lot.reserva_fin != lot.reserva_inicio + timedelta(days=lot.reserva_dias):
                raise ValidationError(_(
                    'La fecha fin se calcula automaticamente y no puede superar '
                    'los %s dias de reserva.') % DIAS_RESERVA)

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
            'reserva_pedido_id': False,
            'reserva_dias': DIAS_RESERVA,
            'asesor_id': False,
        })
        return True
