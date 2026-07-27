# -*- coding: utf-8 -*-
"""
Motor de reportes de almacen para Pierinelli (mismo estilo que los estados
financieros de pierinelli_reportes).

Igual que alla: los montos y fechas se pre-formatean EN PYTHON a claves *_s
(QWeb no permite str.format dentro de web.external_layout) y 'o'/'docs' del
contexto de render deben ser un recordset, nunca el dict de datos.
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockReportWizard(models.TransientModel):
    _name = 'pierinelli.stock.report.wizard'
    _description = 'Asistente de Reportes de Almacen Pierinelli'

    date_from = fields.Date(
        string='Desde',
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(month=1, day=1),
    )
    date_to = fields.Date(
        string='Hasta',
        required=True,
        default=fields.Date.context_today,
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Almacen',
        help='Vacio = todas las sedes.',
    )
    umbral = fields.Float(
        string='Umbral de stock critico (m2)',
        default=100.0,
        help='Los productos con existencias totales por debajo de este valor '
             'aparecen en el reporte de Stock Critico.',
    )
    company_id = fields.Many2one(
        'res.company', string='Compania', required=True,
        default=lambda self: self.env.company,
    )

    # ------------------------------------------------------------------
    #  Utilidades
    # ------------------------------------------------------------------
    @staticmethod
    def _money(value):
        try:
            return '{:,.2f}'.format(value or 0.0)
        except (ValueError, TypeError):
            return '0.00'

    @staticmethod
    def _qty(value):
        try:
            return '{:,.1f}'.format(value or 0.0)
        except (ValueError, TypeError):
            return '0.0'

    @staticmethod
    def _d(value):
        """Fecha (date o datetime) a texto dd/mm/aaaa."""
        return value.strftime('%d/%m/%Y') if value else ''

    def _warehouses(self):
        if self.warehouse_id:
            return self.warehouse_id
        return self.env['stock.warehouse'].search([])

    def _quants(self, warehouse):
        """Quants positivos de las existencias de un almacen."""
        return self.env['stock.quant'].search([
            ('location_id', 'child_of', warehouse.lot_stock_id.id),
            ('quantity', '>', 0),
        ])

    def _moves_done(self):
        """Movimientos realizados en el periodo."""
        return self.env['stock.move'].search([
            ('state', '=', 'done'),
            ('company_id', '=', self.company_id.id),
            ('date', '>=', fields.Datetime.to_datetime(self.date_from)),
            ('date', '<=', fields.Datetime.to_datetime(self.date_to).replace(hour=23, minute=59, second=59)),
            ('product_id.is_storable', '=', True),
        ], order='date, id')

    @staticmethod
    def _move_qty(move):
        return move.quantity or move.product_uom_qty or 0.0

    # ------------------------------------------------------------------
    #  1. Existencias valorizadas por sede
    # ------------------------------------------------------------------
    def _compute_stock_by_warehouse(self):
        sedes = []
        gran_qty = gran_valor = 0.0
        for w in self._warehouses():
            by_prod = {}
            for q in self._quants(w):
                p = q.product_id
                row = by_prod.setdefault(p.id, {
                    'code': p.default_code or '',
                    'name': p.name,
                    'categ': p.categ_id.name or '',
                    'qty': 0.0,
                    'costo': p.standard_price or 0.0,
                    'valor': 0.0,
                })
                row['qty'] += q.quantity
                row['valor'] += q.quantity * (p.standard_price or 0.0)
            lines = sorted(by_prod.values(), key=lambda r: -r['valor'])
            for r in lines:
                r['qty_s'] = self._qty(r['qty'])
                r['costo_s'] = self._money(r['costo'])
                r['valor_s'] = self._money(r['valor'])
            t_qty = sum(r['qty'] for r in lines)
            t_val = sum(r['valor'] for r in lines)
            gran_qty += t_qty
            gran_valor += t_val
            sedes.append({
                'name': w.name,
                'code': w.code,
                'lines': lines,
                'total_qty_s': self._qty(t_qty),
                'total_valor_s': self._money(t_val),
            })
        return {
            'sedes': sedes,
            'gran_qty_s': self._qty(gran_qty),
            'gran_valor_s': self._money(gran_valor),
        }

    # ------------------------------------------------------------------
    #  2. Composicion del inventario por categoria
    # ------------------------------------------------------------------
    def _compute_by_category(self):
        by_cat = {}
        total_valor = total_qty = 0.0
        for w in self._warehouses():
            for q in self._quants(w):
                p = q.product_id
                row = by_cat.setdefault(p.categ_id.id, {
                    'name': p.categ_id.name or '(Sin categoria)',
                    'qty': 0.0, 'valor': 0.0, 'productos': set(),
                })
                row['qty'] += q.quantity
                row['valor'] += q.quantity * (p.standard_price or 0.0)
                row['productos'].add(p.id)
                total_qty += q.quantity
                total_valor += q.quantity * (p.standard_price or 0.0)
        rows = sorted(by_cat.values(), key=lambda r: -r['valor'])
        for r in rows:
            r['n_prod'] = len(r.pop('productos'))
            r['pct'] = (r['valor'] / total_valor * 100.0) if total_valor else 0.0
            r['qty_s'] = self._qty(r['qty'])
            r['valor_s'] = self._money(r['valor'])
            r['pct_s'] = '{:,.1f}%'.format(r['pct'])
        return {
            'rows': rows,
            'total_qty_s': self._qty(total_qty),
            'total_valor_s': self._money(total_valor),
        }

    # ------------------------------------------------------------------
    #  3. Stock critico (productos bajo el umbral)
    # ------------------------------------------------------------------
    def _compute_critical(self):
        warehouses = self.env['stock.warehouse'].search([])
        # cantidades por producto y sede
        per_wh = {}
        totals = {}
        for w in warehouses:
            for q in self._quants(w):
                pid = q.product_id.id
                per_wh.setdefault(pid, {}).setdefault(w.code, 0.0)
                per_wh[pid][w.code] += q.quantity
                totals[pid] = totals.get(pid, 0.0) + q.quantity
        rows = []
        productos = self.env['product.product'].search([('is_storable', '=', True)])
        for p in productos:
            qty = totals.get(p.id, 0.0)
            if qty < self.umbral:
                by_wh = per_wh.get(p.id, {})
                rows.append({
                    'code': p.default_code or '',
                    'name': p.name,
                    'categ': p.categ_id.name or '',
                    'qty': qty,
                    'qty_s': self._qty(qty),
                    'by_wh': {w.code: self._qty(by_wh.get(w.code, 0.0)) for w in warehouses},
                    'agotado': qty <= 0,
                })
        rows.sort(key=lambda r: r['qty'])
        return {
            'rows': rows,
            'wh_codes': [w.code for w in warehouses],
            'umbral_s': self._qty(self.umbral),
            'n_agotados': sum(1 for r in rows if r['agotado']),
        }

    # ------------------------------------------------------------------
    #  4. Antiguedad del inventario (dias en almacen segun fecha de entrada)
    # ------------------------------------------------------------------
    def _compute_stock_aging(self):
        now = fields.Datetime.now()
        buckets = ['b30', 'b90', 'b180', 'mas180']
        by_prod = {}
        for w in self._warehouses():
            for q in self._quants(w):
                p = q.product_id
                row = by_prod.setdefault(p.id, {
                    'code': p.default_code or '',
                    'name': p.name,
                    'b30': 0.0, 'b90': 0.0, 'b180': 0.0, 'mas180': 0.0,
                    'total': 0.0, 'valor': 0.0,
                })
                dias = (now - q.in_date).days if q.in_date else 0
                if dias <= 30:
                    key = 'b30'
                elif dias <= 90:
                    key = 'b90'
                elif dias <= 180:
                    key = 'b180'
                else:
                    key = 'mas180'
                row[key] += q.quantity
                row['total'] += q.quantity
                row['valor'] += q.quantity * (p.standard_price or 0.0)
        rows = sorted(by_prod.values(), key=lambda r: -r['valor'])
        keys = buckets + ['total']
        totals = {b: sum(r[b] for r in rows) for b in keys}
        for r in rows:
            for k in keys:
                r[k + '_s'] = self._qty(r[k])
            r['valor_s'] = self._money(r['valor'])
        totals_s = {b + '_s': self._qty(totals[b]) for b in keys}
        total_valor = sum(r['valor'] for r in rows)
        return {
            'rows': rows,
            'totals': {**totals, **totals_s, 'valor_s': self._money(total_valor)},
        }

    # ------------------------------------------------------------------
    #  5. Kardex de movimientos por producto (entradas/salidas del periodo)
    # ------------------------------------------------------------------
    def _compute_kardex(self):
        by_prod = {}
        for m in self._moves_done():
            src_int = m.location_id.usage == 'internal'
            dst_int = m.location_dest_id.usage == 'internal'
            qty = self._move_qty(m)
            if dst_int and not src_int:
                tipo, ent, sal = 'Entrada', qty, 0.0
            elif src_int and not dst_int:
                tipo, ent, sal = 'Salida', 0.0, qty
            elif src_int and dst_int:
                tipo, ent, sal = 'Traslado', 0.0, 0.0
            else:
                continue
            p = m.product_id
            row = by_prod.setdefault(p.id, {
                'code': p.default_code or '',
                'name': p.name,
                'lines': [],
                'ent': 0.0,
                'sal': 0.0,
            })
            row['ent'] += ent
            row['sal'] += sal
            row['lines'].append({
                'fecha': self._d(m.date),
                'doc': m.reference or (m.picking_id.name if m.picking_id else ''),
                'tipo': tipo,
                'origen': m.location_id.display_name,
                'destino': m.location_dest_id.display_name,
                'ent_s': self._qty(ent) if ent else '',
                'sal_s': self._qty(sal) if sal else '',
                'qty_s': self._qty(qty),
            })
        productos = sorted(by_prod.values(), key=lambda r: r['code'])
        for r in productos:
            r['ent_s'] = self._qty(r['ent'])
            r['sal_s'] = self._qty(r['sal'])
            r['neto_s'] = self._qty(r['ent'] - r['sal'])
        return {'productos': productos, 'count': len(productos)}

    # ------------------------------------------------------------------
    #  6. Transferencias entre sedes
    # ------------------------------------------------------------------
    def _compute_transfers(self):
        rows = []
        total = 0.0
        for m in self._moves_done():
            if m.location_id.usage != 'internal' or m.location_dest_id.usage != 'internal':
                continue
            wh_from = m.location_id.warehouse_id
            wh_to = m.location_dest_id.warehouse_id
            if not wh_from or not wh_to or wh_from == wh_to:
                continue
            qty = self._move_qty(m)
            total += qty
            rows.append({
                'fecha': self._d(m.date),
                'doc': m.reference or (m.picking_id.name if m.picking_id else ''),
                'producto': '[%s] %s' % (m.product_id.default_code or '', m.product_id.name),
                'origen': '%s (%s)' % (wh_from.name, wh_from.code),
                'destino': '%s (%s)' % (wh_to.name, wh_to.code),
                'qty_s': self._qty(qty),
            })
        return {
            'rows': rows,
            'count': len(rows),
            'total_s': self._qty(total),
        }

    # ------------------------------------------------------------------
    #  7. Rotacion: salidas a clientes y entradas de compras del periodo
    # ------------------------------------------------------------------
    def _compute_rotation(self):
        ventas = {}
        compras = {}
        for m in self._moves_done():
            qty = self._move_qty(m)
            p = m.product_id
            if m.location_dest_id.usage == 'customer':
                row = ventas.setdefault(p.id, {
                    'code': p.default_code or '', 'name': p.name,
                    'categ': p.categ_id.name or '', 'qty': 0.0, 'valor': 0.0,
                })
                row['qty'] += qty
                row['valor'] += qty * (p.list_price or 0.0)
            elif m.location_id.usage == 'supplier':
                row = compras.setdefault(p.id, {
                    'code': p.default_code or '', 'name': p.name,
                    'categ': p.categ_id.name or '', 'qty': 0.0, 'valor': 0.0,
                })
                row['qty'] += qty
                row['valor'] += qty * (p.standard_price or 0.0)

        v_rows = sorted(ventas.values(), key=lambda r: -r['qty'])
        c_rows = sorted(compras.values(), key=lambda r: -r['qty'])
        tv = sum(r['qty'] for r in v_rows) or 1.0
        for r in v_rows:
            r['qty_s'] = self._qty(r['qty'])
            r['valor_s'] = self._money(r['valor'])
            r['pct_s'] = '{:,.1f}%'.format(r['qty'] / tv * 100.0)
        for r in c_rows:
            r['qty_s'] = self._qty(r['qty'])
            r['valor_s'] = self._money(r['valor'])
        return {
            'ventas': v_rows,
            'compras': c_rows,
            'total_ventas_s': self._qty(sum(r['qty'] for r in v_rows)),
            'valor_ventas_s': self._money(sum(r['valor'] for r in v_rows)),
            'total_compras_s': self._qty(sum(r['qty'] for r in c_rows)),
            'valor_compras_s': self._money(sum(r['valor'] for r in c_rows)),
        }

    # ------------------------------------------------------------------
    #  Datos base + acciones
    # ------------------------------------------------------------------
    def _report_header(self):
        return {
            'company': self.company_id.name,
            'ruc': self.company_id.vat or '',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'target_move': ('Sede: %s' % self.warehouse_id.name
                            if self.warehouse_id else 'Todas las sedes'),
        }

    def _build_report_data(self, report_type):
        self.ensure_one()
        computes = {
            'stock_by_warehouse': self._compute_stock_by_warehouse,
            'by_category': self._compute_by_category,
            'critical': self._compute_critical,
            'stock_aging': self._compute_stock_aging,
            'kardex': self._compute_kardex,
            'transfers': self._compute_transfers,
            'rotation': self._compute_rotation,
        }
        if report_type not in computes:
            raise UserError(_('Tipo de reporte desconocido: %s') % report_type)
        return {
            'wizard_id': self.id,
            'header': self._report_header(),
            'report_type': report_type,
            **computes[report_type](),
        }

    def _print(self, xmlid, report_type):
        if self.date_from > self.date_to:
            raise UserError(_('La fecha "Desde" no puede ser posterior a "Hasta".'))
        data = self._build_report_data(report_type)
        return self.env.ref(xmlid).report_action(self, data=data)

    def action_stock_by_warehouse(self):
        return self._print('pierinelli_almacenes.action_report_stock_by_warehouse',
                            'stock_by_warehouse')

    def action_by_category(self):
        return self._print('pierinelli_almacenes.action_report_by_category',
                            'by_category')

    def action_critical(self):
        return self._print('pierinelli_almacenes.action_report_critical',
                            'critical')

    def action_stock_aging(self):
        return self._print('pierinelli_almacenes.action_report_stock_aging',
                            'stock_aging')

    def action_kardex(self):
        return self._print('pierinelli_almacenes.action_report_kardex',
                            'kardex')

    def action_transfers(self):
        return self._print('pierinelli_almacenes.action_report_transfers',
                            'transfers')

    def action_rotation(self):
        return self._print('pierinelli_almacenes.action_report_rotation',
                            'rotation')


class ReportStockByWarehouse(models.AbstractModel):
    _name = 'report.pierinelli_almacenes.report_stock_by_warehouse_doc'
    _description = 'Datos Existencias por Sede'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.stock.report.wizard'].browse(data['wizard_id'])
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}


class ReportByCategory(models.AbstractModel):
    _name = 'report.pierinelli_almacenes.report_by_category_doc'
    _description = 'Datos Composicion por Categoria'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.stock.report.wizard'].browse(data['wizard_id'])
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}


class ReportCritical(models.AbstractModel):
    _name = 'report.pierinelli_almacenes.report_critical_doc'
    _description = 'Datos Stock Critico'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.stock.report.wizard'].browse(data['wizard_id'])
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}


class ReportStockAging(models.AbstractModel):
    _name = 'report.pierinelli_almacenes.report_stock_aging_doc'
    _description = 'Datos Antiguedad del Inventario'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.stock.report.wizard'].browse(data['wizard_id'])
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}


class ReportKardex(models.AbstractModel):
    _name = 'report.pierinelli_almacenes.report_kardex_doc'
    _description = 'Datos Kardex'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.stock.report.wizard'].browse(data['wizard_id'])
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}


class ReportTransfers(models.AbstractModel):
    _name = 'report.pierinelli_almacenes.report_transfers_doc'
    _description = 'Datos Transferencias entre Sedes'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.stock.report.wizard'].browse(data['wizard_id'])
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}


class ReportRotation(models.AbstractModel):
    _name = 'report.pierinelli_almacenes.report_rotation_doc'
    _description = 'Datos Rotacion de Productos'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['pierinelli.stock.report.wizard'].browse(data['wizard_id'])
        return {'doc': data, 'docs': wizard, 'o': wizard, 'wizard': wizard}