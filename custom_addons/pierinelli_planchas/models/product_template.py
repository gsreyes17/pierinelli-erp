# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tipo_material = fields.Selection(
        [('natural', 'Natural'), ('artificial', 'Artificial')],
        string='Tipo de material',
        default='natural',
        help='Natural (marmol, granito, cuarcita, onix): cada plancha es unica '
             'y lleva su propia foto. Artificial (porcelanico, sinterizada): '
             'formato constante, todas comparten la foto del producto.',
    )
    prefijo_plancha = fields.Char(
        string='Prefijo de plancha',
        compute='_compute_prefijo_plancha', store=True, readonly=False,
        help='Iniciales para el codigo interno de cada plancha. Se genera solo '
             'a partir del nombre (Cuarcita Iron Green -> CIG) y es editable.',
    )
    plancha_count = fields.Integer(
        string='Planchas', compute='_compute_plancha_count',
    )

    # Palabras que no aportan inicial al prefijo
    _PALABRAS_OMITIDAS = {'de', 'del', 'la', 'el', 'los', 'las', 'y', 'con', 'a'}

    @api.depends('name')
    def _compute_prefijo_plancha(self):
        for tmpl in self:
            palabras = [
                w for w in (tmpl.name or '').replace('-', ' ').split()
                if w.lower() not in self._PALABRAS_OMITIDAS
            ]
            tmpl.prefijo_plancha = (
                ''.join(w[0] for w in palabras[:4]).upper() or 'PLN'
            )

    def _compute_plancha_count(self):
        grupos = dict(self.env['stock.lot']._read_group(
            [('product_id.product_tmpl_id', 'in', self.ids)],
            ['product_id'], ['__count'],
        ))
        conteo = {}
        for producto, cantidad in grupos.items():
            tmpl_id = producto.product_tmpl_id.id
            conteo[tmpl_id] = conteo.get(tmpl_id, 0) + cantidad
        for tmpl in self:
            tmpl.plancha_count = conteo.get(tmpl.id, 0)

    def action_ver_planchas(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'pierinelli_planchas.action_planchas_operaciones')
        action['domain'] = [('product_id.product_tmpl_id', '=', self.id)]
        action['context'] = {'default_product_id': self.product_variant_id.id}
        return action
