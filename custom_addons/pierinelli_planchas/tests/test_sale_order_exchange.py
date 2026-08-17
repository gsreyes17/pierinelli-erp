# -*- coding: utf-8 -*-
from odoo import fields
from odoo.tests.common import TransactionCase


class TestSaleOrderExchangeRate(TransactionCase):
    def test_quote_rate_is_transferred_to_invoice(self):
        company = self.env.company
        usd = self.env.ref('base.USD')
        partner = self.env['res.partner'].create({
            'name': 'Cliente USD de prueba', 'company_id': company.id})
        pricelist = self.env['product.pricelist'].create({
            'name': 'USD prueba de cotización', 'currency_id': usd.id,
            'company_id': company.id,
        })
        today = fields.Date.context_today(self.env['sale.order'])
        rate_model = self.env['pierinelli.tipo.cambio']
        rate = rate_model.search([
            ('fecha', '=', today), ('origen', '=', 'corporativa')], limit=1)
        if not rate:
            rate = rate_model.create({
                'fecha': today, 'origen': 'corporativa', 'compra': 3.70,
                'venta': 3.75,
            })
        order = self.env['sale.order'].create({
            'partner_id': partner.id, 'pricelist_id': pricelist.id,
            'origen_tasa': 'corporativa',
        })
        order._onchange_origen_tasa()
        self.assertEqual(order.currency_id, usd)
        self.assertEqual(order.tasa_aplicada, rate.venta)
        values = order._prepare_invoice()
        self.assertEqual(values['origen_tasa'], 'corporativa')
        self.assertEqual(values['tasa_aplicada'], rate.venta)
        self.assertAlmostEqual(values['invoice_currency_rate'], 1.0 / rate.venta)

    def test_usd_pricelist_uses_fixed_product_price_not_zero_global_rule(self):
        usd = self.env.ref('base.USD')
        pricelist = self.env['product.pricelist'].create({
            'name': 'USD precio fijo de prueba', 'currency_id': usd.id,
            'company_id': self.env.company.id,
        })
        product = self.env['product.product'].search([
            ('sale_ok', '=', True)], limit=1)
        self.env['product.pricelist.item'].create({
            'pricelist_id': pricelist.id, 'applied_on': '1_product',
            'product_id': product.id, 'compute_price': 'fixed', 'fixed_price': 100.0,
        })
        price = pricelist._get_product_price(
            product, 1.0, currency=usd, date=fields.Date.context_today(pricelist))
        self.assertEqual(price, 100.0)
