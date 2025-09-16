# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    coupon_code = fields.Char('Coupon Code')
    delivery_notes = fields.Text('Delivery Notes')
    gift_message = fields.Text('Gift Message')
    is_gift = fields.Boolean('Is Gift Order', default=False)

    @api.model
    def get_cart_summary(self):
        order = self.env['website'].get_current_website().sale_get_order()
        if not order:
            return {
                'cart_quantity': 0,
                'amount_total': 0,
                'currency_symbol': self.env.company.currency_id.symbol,
                'order_lines': []
            }

        return {
            'cart_quantity': sum(order.order_line.mapped('product_uom_qty')),
            'amount_total': order.amount_total,
            'currency_symbol': order.currency_id.symbol,
            'order_lines': [{
                'id': line.id,
                'name': line.product_id.name,
                'quantity': line.product_uom_qty,
                'price_unit': line.price_unit,
                'price_total': line.price_total,
                'product_image': line.product_id.image_1920,
            } for line in order.order_line]
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    gift_wrap = fields.Boolean('Gift Wrap', default=False)
    gift_wrap_message = fields.Text('Gift Wrap Message')