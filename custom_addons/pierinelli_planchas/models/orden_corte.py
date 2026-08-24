# -*- coding: utf-8 -*-
"""
Orden de Produccion / Corte y registro de mermas (Plan V2, Fase 4).

Flujo del cliente: tras la factura se emite una Orden de Produccion con las
medidas de los cortes y la modulacion (PDFs de AutoCAD) anexa. Una orden puede
cubrir VARIAS planchas del mismo pedido: cada plancha es una seccion con su
propio listado de cortes, su retorno y su merma con destino propio.

Al ejecutar, POR CADA plancha de la orden:

    Plancha CIG1025.01 (5.61 m²)
      ├── vendido al cliente      (queda en la plancha; sale por la entrega)
      ├── retorno a stock .01.01  (lote nuevo con medidas menores)
      └── merma                   (Zona de Mermas, fuera de la vista de ventas)

La merma registra su destino: asumida por el cliente (metro lineal) o perdida
del negocio (corte por bloques), y puede reingresarse si resulta aprovechable.

Nota de compatibilidad: hasta la v1.1 la orden era de UNA plancha con los
campos plancha_id/retorno_*/destino_merma en la cabecera. Esos campos se
conservan como legado (la migracion 19.0.1.2.0 los convierte en la primera
seccion) y el create() acepta el formato viejo creando la seccion equivalente.
"""
import base64

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import pdf as pdf_tools


MOTIVOS_MERMA = [
    ('corte', 'Corte de plancha'),
    ('rotura', 'Rotura en manipulacion'),
    ('defecto', 'Defecto del material'),
    ('muestra', 'Muestra / exhibicion'),
    ('otro', 'Otro'),
]

DESTINOS_MERMA = [
    ('cliente', 'Asumida por el cliente (metro lineal)'),
    ('negocio', 'Perdida del negocio (corte por bloques)'),
]


def get_location_mermas(env):
    """Zona de Mermas: se crea al primer uso (en v19 las ubicaciones
    virtuales no tienen xmlid estable). Es tipo 'perdida de inventario':
    lo que entra sale del stock vendible pero conserva su plancha."""
    Location = env['stock.location'].sudo()
    loc = Location.search([
        ('name', '=', 'Zona de Mermas'), ('usage', '=', 'inventory'),
        ('company_id', 'in', (env.company.id, False)),
    ], limit=1)
    if not loc:
        padre = Location.search([
            ('usage', '=', 'inventory'),
            ('company_id', 'in', (env.company.id, False)),
        ], limit=1)
        loc = Location.create({
            'name': 'Zona de Mermas',
            'usage': 'inventory',
            'location_id': padre.location_id.id if padre else False,
            'company_id': env.company.id,
        })
    return loc


class OrdenCorte(models.Model):
    _name = 'pierinelli.orden.corte'
    _description = 'Orden de Produccion / Corte'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Numero', default='Nuevo', readonly=True, copy=False)
    state = fields.Selection(
        [('borrador', 'Borrador'), ('hecho', 'Hecho'),
         ('cancelada', 'Cancelada')],
        default='borrador', tracking=True, string='Estado')
    fecha = fields.Date(default=fields.Date.context_today, required=True)

    plancha_ids = fields.One2many(
        'pierinelli.orden.corte.plancha', 'orden_id',
        string='Planchas a cortar')
    plancha_count = fields.Integer(compute='_compute_totales', store=True)

    sale_order_id = fields.Many2one(
        'sale.order', string='Pedido de venta',
        help='Pedido que origina el corte. Lo cortado queda en cada plancha '
             'y sale al cliente por la entrega de ese pedido.')
    partner_id = fields.Many2one(
        'res.partner', string='Cliente',
        compute='_compute_partner', store=True, readonly=False)
    asesor_id = fields.Many2one(
        'res.users', string='Asesor',
        default=lambda self: self.env.user)

    # Totales sobre todas las secciones
    m2_cortes = fields.Float(
        'm² a cortar (venta)', compute='_compute_totales', store=True,
        digits=(8, 2))
    m2_retorno = fields.Float(
        'm² retorno a stock', compute='_compute_totales', store=True,
        digits=(8, 2))
    m2_merma = fields.Float(
        'm² merma', compute='_compute_totales', store=True, digits=(8, 2))

    modulacion_ids = fields.Many2many(
        'ir.attachment', string='Modulacion (PDF)',
        help='Disenos de AutoCAD exportados a PDF. Se anexan al final del '
             'PDF de la orden.')
    notas = fields.Text('Notas')

    # ---- Campos LEGADO (orden de una sola plancha, hasta v1.1) ----
    # Se mantienen para no perder datos hasta migrar y para aceptar el
    # formato viejo de creacion; la vista ya no los muestra.
    plancha_id = fields.Many2one(
        'stock.lot', string='Plancha (legado)',
        help='Referencia de la epoca de una plancha por orden; hoy la '
             'primera plancha de la orden. Usar plancha_ids.')
    linea_ids = fields.One2many(
        'pierinelli.orden.corte.linea', 'orden_id',
        string='Cortes (legado)')
    retorno_largo = fields.Float('Retorno: largo (m) (legado)', digits=(6, 2))
    retorno_alto = fields.Float('Retorno: alto (m) (legado)', digits=(6, 2))
    destino_merma = fields.Selection(
        DESTINOS_MERMA, string='Destino de la merma (legado)',
        default='negocio')
    plancha_retorno_id = fields.Many2one(
        'stock.lot', string='Plancha retorno (legado)', readonly=True,
        copy=False,
        help='Retorno de la primera seccion; cada seccion tiene el suyo.')

    @api.depends('sale_order_id', 'plancha_ids.plancha_id')
    def _compute_partner(self):
        for orden in self:
            primera = orden.plancha_ids[:1].plancha_id
            orden.partner_id = (orden.sale_order_id.partner_id
                                or primera.cliente_reserva_id
                                or orden.partner_id)

    @api.depends('plancha_ids', 'plancha_ids.m2_cortes',
                 'plancha_ids.m2_retorno', 'plancha_ids.m2_merma')
    def _compute_totales(self):
        for orden in self:
            orden.plancha_count = len(orden.plancha_ids)
            orden.m2_cortes = round(
                sum(orden.plancha_ids.mapped('m2_cortes')), 2)
            orden.m2_retorno = round(
                sum(orden.plancha_ids.mapped('m2_retorno')), 2)
            orden.m2_merma = round(
                sum(orden.plancha_ids.mapped('m2_merma')), 2)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = (self.env['ir.sequence']
                                .next_by_code('pierinelli.orden.corte')
                                or 'OP-00000')
            # Compatibilidad con el formato de UNA plancha: si llega el
            # campo viejo y no hay secciones, se convierte en la primera.
            if vals.get('plancha_id') and not vals.get('plancha_ids'):
                vals['plancha_ids'] = [(0, 0, {
                    'plancha_id': vals['plancha_id'],
                    'retorno_largo': vals.pop('retorno_largo', 0.0),
                    'retorno_alto': vals.pop('retorno_alto', 0.0),
                    'destino_merma': vals.pop('destino_merma', 'negocio')
                    or 'negocio',
                    'linea_ids': vals.pop('linea_ids', []),
                })]
        ordenes = super().create(vals_list)
        ordenes._sync_legacy()
        return ordenes

    def _sync_legacy(self):
        """Mantiene los campos legado apuntando a la primera seccion, para
        que busquedas y codigo antiguos sigan encontrando algo coherente."""
        for orden in self:
            primera = orden.plancha_ids[:1]
            valores = {}
            if orden.plancha_id != primera.plancha_id:
                valores['plancha_id'] = primera.plancha_id.id or False
            if orden.plancha_retorno_id != primera.plancha_retorno_id:
                valores['plancha_retorno_id'] = (
                    primera.plancha_retorno_id.id or False)
            if valores:
                orden.write(valores)

    # ------------------------------------------------------------------
    #  Confirmar: ejecutar el corte de TODAS las planchas
    # ------------------------------------------------------------------
    def _location_mermas(self):
        return get_location_mermas(self.env)

    def action_confirmar(self):
        for orden in self:
            if orden.state != 'borrador':
                continue
            if not orden.plancha_ids:
                raise UserError(_(
                    'Agrega al menos una plancha con sus cortes.'))
            # Validar TODO antes de mover nada: si una plancha falla,
            # ninguna se corta a medias.
            for seccion in orden.plancha_ids:
                seccion._validar()
            # El estado pasa a 'hecho' ANTES de mover stock: el compute de
            # m2_merma se congela con ese estado, y asi los movimientos de
            # quants no re-disparan un recalculo con el disponible ya
            # cambiado (mismo criterio que tenia la version de una plancha).
            orden.state = 'hecho'
            for seccion in orden.plancha_ids:
                seccion._ejecutar()
            orden._sync_legacy()
            orden.message_post(body=_(
                'Corte ejecutado sobre %(n)d plancha(s): %(v).2f m² para '
                'venta, %(r).2f m² de retorno, %(m).2f m² de merma.',
                n=len(orden.plancha_ids), v=orden.m2_cortes,
                r=orden.m2_retorno, m=orden.m2_merma))
        return True

    def action_cancelar(self):
        for orden in self:
            if orden.state == 'hecho':
                raise UserError(_(
                    'La orden %s ya fue ejecutada; el corte no se deshace '
                    'desde aqui.') % orden.name)
            orden.state = 'cancelada'

    # ------------------------------------------------------------------
    #  PDF con la modulacion anexa
    # ------------------------------------------------------------------
    def action_imprimir(self):
        """Genera el PDF de la orden y le anexa la modulacion (PDFs)."""
        self.ensure_one()
        report = self.env.ref('pierinelli_planchas.action_report_orden_corte')
        contenido, _tipo = self.env['ir.actions.report']._render_qweb_pdf(
            report, res_ids=self.ids)
        pdfs = [contenido]
        for adjunto in self.modulacion_ids:
            if adjunto.mimetype == 'application/pdf' and adjunto.datas:
                pdfs.append(base64.b64decode(adjunto.datas))
        if len(pdfs) > 1:
            try:
                contenido = pdf_tools.merge_pdf(pdfs)
            except Exception:
                pass    # si un anexo esta danado, se entrega la OP sola
        att = self.env['ir.attachment'].create({
            'name': '%s.pdf' % self.name,
            'raw': contenido,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%d?download=true' % att.id,
            'target': 'self',
        }


class OrdenCortePlancha(models.Model):
    _name = 'pierinelli.orden.corte.plancha'
    _description = 'Plancha dentro de una orden de corte'
    _order = 'orden_id, id'

    orden_id = fields.Many2one(
        'pierinelli.orden.corte', required=True, ondelete='cascade')
    state = fields.Selection(related='orden_id.state', store=True)
    plancha_id = fields.Many2one(
        'stock.lot', string='Plancha', required=True,
        domain="[('m2_disponible', '>', 0)]")
    product_id = fields.Many2one(
        related='plancha_id.product_id', string='Material')
    m2_plancha = fields.Float(
        related='plancha_id.m2_disponible', string='m² disponibles')

    linea_ids = fields.One2many(
        'pierinelli.orden.corte.linea', 'seccion_id', string='Cortes')
    m2_cortes = fields.Float(
        'm² a cortar', compute='_compute_m2', store=True, digits=(8, 2))
    retorno_largo = fields.Float('Retorno: largo (m)', digits=(6, 2))
    retorno_alto = fields.Float('Retorno: alto (m)', digits=(6, 2))
    m2_retorno = fields.Float(
        'm² retorno', compute='_compute_m2', store=True, digits=(8, 2))
    m2_merma = fields.Float(
        'm² merma', compute='_compute_m2', store=True, digits=(8, 2),
        help='Lo que no es corte vendido ni retorno: se va a la Zona de '
             'Mermas al ejecutar. Decide su destino ANTES de ejecutar.')
    destino_merma = fields.Selection(
        DESTINOS_MERMA, string='Destino de la merma',
        default='negocio', required=True)
    plancha_retorno_id = fields.Many2one(
        'stock.lot', string='Plancha retorno', readonly=True, copy=False)

    @api.depends('linea_ids.m2', 'retorno_largo', 'retorno_alto',
                 'plancha_id.m2_disponible', 'orden_id.state')
    def _compute_m2(self):
        for sec in self:
            sec.m2_cortes = round(sum(sec.linea_ids.mapped('m2')), 2)
            sec.m2_retorno = round(
                (sec.retorno_largo or 0) * (sec.retorno_alto or 0), 2)
            if sec.orden_id.state == 'hecho':
                # ya ejecutada: la merma quedo fijada, no se recalcula
                continue
            sec.m2_merma = round(
                (sec.plancha_id.m2_disponible or 0)
                - sec.m2_cortes - sec.m2_retorno, 2)

    @api.constrains('linea_ids', 'retorno_largo', 'retorno_alto',
                    'plancha_id')
    def _check_m2(self):
        for sec in self.filtered(lambda s: s.orden_id.state == 'borrador'):
            if sec.m2_merma < -0.01:
                raise ValidationError(_(
                    'Plancha %(p)s: los cortes (%(c).2f m²) + el retorno '
                    '(%(r).2f m²) superan lo disponible (%(d).2f m²).',
                    p=sec.plancha_id.name, c=sec.m2_cortes,
                    r=sec.m2_retorno, d=sec.plancha_id.m2_disponible))

    @api.constrains('plancha_id', 'orden_id')
    def _check_plancha_unica(self):
        for sec in self:
            repetidas = sec.orden_id.plancha_ids.filtered(
                lambda s: s.plancha_id == sec.plancha_id)
            if len(repetidas) > 1:
                raise ValidationError(_(
                    'La plancha %s aparece dos veces en la orden; junta '
                    'sus cortes en una sola seccion.') % sec.plancha_id.name)

    def _validar(self):
        self.ensure_one()
        if not self.linea_ids:
            raise UserError(_(
                'Plancha %s: agrega al menos un corte con sus medidas.')
                % self.plancha_id.name)
        if self.m2_merma < -0.01:
            raise UserError(_(
                'Plancha %s: los cortes superan lo disponible.')
                % self.plancha_id.name)
        quant = self.plancha_id.quant_ids.filtered(
            lambda q: q.location_id.usage == 'internal' and q.quantity > 0)
        if not quant:
            raise UserError(_(
                'La plancha %s no tiene stock en ninguna ubicacion.')
                % self.plancha_id.name)

    def _ejecutar(self):
        """El corte fisico de UNA plancha (la logica probada de siempre)."""
        self.ensure_one()
        Quant = self.env['stock.quant']
        orden = self.orden_id
        plancha = self.plancha_id
        ubicacion = plancha.quant_ids.filtered(
            lambda q: q.location_id.usage == 'internal'
            and q.quantity > 0)[:1].location_id

        # Congelar cantidades ANTES de mover stock: m2_merma se calcula
        # sobre lo disponible, que cambia con cada movimiento.
        m2_retorno = self.m2_retorno
        m2_merma = self.m2_merma

        # 1) Retorno: nace la plancha hija con codigo extendido
        if m2_retorno > 0.005:
            hija = self.env['stock.lot'].create({
                'name': plancha.siguiente_codigo_corte(),
                'product_id': plancha.product_id.id,
                'company_id': plancha.company_id.id,
                'largo': self.retorno_largo,
                'alto': self.retorno_alto,
                'espesor': plancha.espesor,
                'm2_neto': m2_retorno,
                'condicion': plancha.condicion,
                'ubicacion_ref': plancha.ubicacion_ref,
                'ref_importacion': plancha.ref_importacion,
                'fecha_ingreso': fields.Date.context_today(self),
                'plancha_madre_id': plancha.id,
                'image_1920': plancha.image_1920 or False,
            })
            Quant._update_available_quantity(
                plancha.product_id, ubicacion, -m2_retorno, lot_id=plancha)
            Quant._update_available_quantity(
                plancha.product_id, ubicacion, m2_retorno, lot_id=hija)
            self.plancha_retorno_id = hija
            hija.message_post(body=_(
                'Retorno del corte %(op)s de la plancha %(madre)s '
                '(%(m2).2f m²).', op=orden.name, madre=plancha.name,
                m2=m2_retorno))

        # 2) Merma: sale a la Zona de Mermas (fuera de la vista de ventas)
        if m2_merma > 0.005:
            Quant._update_available_quantity(
                plancha.product_id, ubicacion, -m2_merma, lot_id=plancha)
            Quant._update_available_quantity(
                plancha.product_id, orden._location_mermas(), m2_merma,
                lot_id=plancha)
            self.env['pierinelli.merma'].create({
                'plancha_id': plancha.id,
                'orden_corte_id': orden.id,
                'm2': m2_merma,
                'motivo': 'corte',
                'destino': self.destino_merma,
                'warehouse_id': (ubicacion.warehouse_id.id
                                 if ubicacion.warehouse_id else False),
            })

        plancha.message_post(body=_(
            'Corte %(op)s ejecutado: %(v).2f m² para venta, '
            '%(r).2f m² de retorno, %(m).2f m² de merma (%(dest)s).',
            op=orden.name, v=self.m2_cortes, r=m2_retorno,
            m=max(m2_merma, 0.0),
            dest=dict(self._fields['destino_merma'].selection)
                [self.destino_merma]))
        self.m2_merma = max(m2_merma, 0.0)


class OrdenCorteLinea(models.Model):
    _name = 'pierinelli.orden.corte.linea'
    _description = 'Corte de una orden de produccion'

    seccion_id = fields.Many2one(
        'pierinelli.orden.corte.plancha', ondelete='cascade',
        string='Plancha de la orden')
    orden_id = fields.Many2one(
        'pierinelli.orden.corte', ondelete='cascade',
        string='Orden',
        help='Se completa solo desde la seccion; queda tambien aqui por '
             'compatibilidad con las ordenes previas a las secciones.')
    descripcion = fields.Char(
        'Pieza', required=True,
        help='Ej. "Encimera cocina", "Isla central", "Salpicadero".')
    cantidad = fields.Integer('Piezas', default=1, required=True)
    largo = fields.Float('Largo (m)', digits=(6, 2), required=True)
    alto = fields.Float('Alto (m)', digits=(6, 2), required=True)
    m2 = fields.Float('m²', compute='_compute_m2', store=True, digits=(8, 2))

    @api.depends('cantidad', 'largo', 'alto')
    def _compute_m2(self):
        for linea in self:
            linea.m2 = round(
                (linea.cantidad or 0) * (linea.largo or 0)
                * (linea.alto or 0), 2)

    @api.model_create_multi
    def create(self, vals_list):
        lineas = super().create(vals_list)
        for linea in lineas:
            if linea.seccion_id and not linea.orden_id:
                linea.orden_id = linea.seccion_id.orden_id
        return lineas


class Merma(models.Model):
    _name = 'pierinelli.merma'
    _description = 'Registro de merma'
    _order = 'fecha desc, id desc'

    name = fields.Char(compute='_compute_name')
    fecha = fields.Date(default=fields.Date.context_today, required=True)
    plancha_id = fields.Many2one('stock.lot', string='Plancha', required=True)
    product_id = fields.Many2one(
        related='plancha_id.product_id', string='Material', store=True)
    orden_corte_id = fields.Many2one(
        'pierinelli.orden.corte', string='Orden de corte')
    plancha_reingreso_id = fields.Many2one(
        'stock.lot', string='Plancha de reingreso', readonly=True,
        copy=False,
        help='Nueva plancha creada al recuperar esta merma. Conserva la '
             'trazabilidad sin devolver el material al lote ya cortado.')
    m2 = fields.Float('m²', digits=(8, 2), required=True)
    valor = fields.Float(
        'Valor (S/)', digits=(12, 2),
        compute='_compute_valor', store=True,
        help='m² de merma x costo kardex del material al momento.')
    motivo = fields.Selection(MOTIVOS_MERMA, required=True, default='corte')
    destino = fields.Selection(
        [('cliente', 'Asumida por el cliente'),
         ('negocio', 'Perdida del negocio'),
         ('reingreso', 'Reingresada a stock')],
        required=True, default='negocio')
    warehouse_id = fields.Many2one('stock.warehouse', string='Sede')
    notas = fields.Char('Notas')

    def _compute_name(self):
        for merma in self:
            merma.name = 'Merma %s (%.2f m²)' % (
                merma.plancha_id.name or '', merma.m2)

    @api.depends('m2', 'plancha_id')
    def _compute_valor(self):
        for merma in self:
            merma.valor = round(
                merma.m2 * (merma.plancha_id.product_id.standard_price or 0), 2)

    def action_reingresar(self):
        """La merma resulto aprovechable: vuelve al stock de su sede."""
        Quant = self.env['stock.quant']
        loc_mermas = get_location_mermas(self.env)
        for merma in self:
            if merma.destino == 'reingreso':
                raise UserError(_('Esta merma ya fue reingresada.'))
            destino = (merma.warehouse_id.lot_stock_id
                       if merma.warehouse_id
                       else self.env['stock.warehouse'].search([], limit=1)
                       .lot_stock_id)
            Quant._update_available_quantity(
                merma.plancha_id.product_id, loc_mermas, -merma.m2,
                lot_id=merma.plancha_id)
            Quant._update_available_quantity(
                merma.plancha_id.product_id, destino, merma.m2,
                lot_id=merma.plancha_id)
            merma.destino = 'reingreso'
            merma.plancha_id.message_post(body=_(
                'Merma de %(m2).2f m² reingresada a stock en %(sede)s.',
                m2=merma.m2, sede=destino.display_name))
