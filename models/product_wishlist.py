# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductWishlist(models.Model):
    _name = 'product.wishlist'
    _description = 'Product Wishlist'
    _rec_name = 'product_id'

    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)
    product_id = fields.Many2one('product.template', string='Product', required=True)
    date_added = fields.Datetime('Date Added', default=fields.Datetime.now)

    _sql_constraints = [
        ('unique_user_product', 'unique(user_id, product_id)', 'Product already in wishlist!')
    ]

    @api.model
    def toggle_wishlist(self, product_id):
        existing = self.search([('user_id', '=', self.env.user.id), ('product_id', '=', product_id)])
        if existing:
            existing.unlink()
            return {'in_wishlist': False}
        else:
            self.create({'product_id': product_id})
            return {'in_wishlist': True}

    @api.model
    def is_in_wishlist(self, product_id):
        return bool(self.search([('user_id', '=', self.env.user.id), ('product_id', '=', product_id)]))


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def get_wishlist_products(self, limit=20):
        wishlist_items = self.env['product.wishlist'].search([
            ('user_id', '=', self.env.user.id)
        ], limit=limit, order='date_added desc')
        return wishlist_items.product_id