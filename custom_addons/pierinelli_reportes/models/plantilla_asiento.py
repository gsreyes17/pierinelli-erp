# -*- coding: utf-8 -*-
"""
Plantillas de asientos contables (Plan V2, Fase 5 tarea 25).

Odoo Community trae asientos recurrentes (auto_post) pero no plantillas
reutilizables a demanda. Aqui el contador define una vez las lineas (cuenta,
lado, monto fijo o % de un importe base) y luego genera el asiento en dos
clics: elige plantilla, fecha e importe, y sale el borrador cuadrado.
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PlantillaAsiento(models.Model):
    _name = 'pierinelli.plantilla.asiento'
    _description = 'Plantilla de asiento contable'

    name = fields.Char('Nombre', required=True)
    journal_id = fields.Many2one(
        'account.journal', string='Diario', required=True,
        domain=[('type', '=', 'general')],
        default=lambda self: self.env['account.journal'].search(
            [('type', '=', 'general')], limit=1))
    descripcion = fields.Char(
        'Descripcion', help='Para que sirve esta plantilla.')
    linea_ids = fields.One2many(
        'pierinelli.plantilla.asiento.linea', 'plantilla_id',
        string='Lineas')
    active = fields.Boolean(default=True)

    def action_usar(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generar asiento: %s') % self.name,
            'res_model': 'pierinelli.plantilla.usar',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_plantilla_id': self.id},
        }


class PlantillaAsientoLinea(models.Model):
    _name = 'pierinelli.plantilla.asiento.linea'
    _description = 'Linea de plantilla de asiento'
    _order = 'sequence, id'

    plantilla_id = fields.Many2one(
        'pierinelli.plantilla.asiento', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    account_id = fields.Many2one(
        'account.account', string='Cuenta', required=True)
    name = fields.Char('Glosa', required=True)
    lado = fields.Selection(
        [('debe', 'Debe'), ('haber', 'Haber')], required=True,
        default='debe')
    modo = fields.Selection(
        [('porcentaje', '% del importe base'), ('fijo', 'Monto fijo')],
        required=True, default='porcentaje')
    valor = fields.Float(
        'Valor', required=True, digits=(12, 2),
        help='Porcentaje (ej. 100, 18, 9.5) o monto fijo en soles.')


class PlantillaUsar(models.TransientModel):
    _name = 'pierinelli.plantilla.usar'
    _description = 'Generar asiento desde plantilla'

    plantilla_id = fields.Many2one(
        'pierinelli.plantilla.asiento', string='Plantilla', required=True)
    fecha = fields.Date(
        default=fields.Date.context_today, required=True)
    ref = fields.Char('Referencia')
    importe_base = fields.Float(
        'Importe base (S/)', digits=(12, 2),
        help='Sobre este monto se calculan las lineas porcentuales '
             '(ej. el total de la planilla del mes).')

    def action_generar(self):
        self.ensure_one()
        plantilla = self.plantilla_id
        if not plantilla.linea_ids:
            raise UserError(_('La plantilla no tiene lineas.'))
        usa_pct = any(l.modo == 'porcentaje' for l in plantilla.linea_ids)
        if usa_pct and self.importe_base <= 0:
            raise UserError(_(
                'Esta plantilla usa porcentajes: indica el importe base.'))

        lineas = []
        total_debe = total_haber = 0.0
        for linea in plantilla.linea_ids:
            monto = (round(self.importe_base * linea.valor / 100.0, 2)
                     if linea.modo == 'porcentaje' else linea.valor)
            debe = monto if linea.lado == 'debe' else 0.0
            haber = monto if linea.lado == 'haber' else 0.0
            total_debe += debe
            total_haber += haber
            lineas.append((0, 0, {
                'account_id': linea.account_id.id,
                'name': linea.name,
                'debit': debe,
                'credit': haber,
            }))
        if abs(total_debe - total_haber) > 0.01:
            raise UserError(_(
                'El asiento no cuadra: Debe %(d).2f vs Haber %(h).2f. '
                'Revisa los valores de la plantilla.',
                d=total_debe, h=total_haber))

        move = self.env['account.move'].create({
            'move_type': 'entry',
            'journal_id': plantilla.journal_id.id,
            'date': self.fecha,
            'ref': self.ref or plantilla.name,
            'line_ids': lineas,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
        }
