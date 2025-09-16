# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductWishlist(models.Model):
    _name = 'product.wishlist'
    _description = 'Product Wishlist'
    _rec_name = 'product_id'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True,
                                default=lambda self: self.env.user.partner_id)
    product_id = fields.Many2one('product.template', string='Product', required=True)
    date_added = fields.Datetime('Date Added', default=fields.Datetime.now)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('unique_partner_product', 'unique(partner_id, product_id)', 'Product already in wishlist!')
    ]

    @api.model
    def toggle_wishlist(self, product_id):
        partner_id = self.env.user.partner_id.id
        existing = self.search([('partner_id', '=', partner_id), ('product_id', '=', product_id)])
        if existing:
            existing.unlink()
            return {'in_wishlist': False}
        else:
            self.create({'product_id': product_id, 'partner_id': partner_id})
            return {'in_wishlist': True}

    @api.model
    def is_in_wishlist(self, product_id):
        partner_id = self.env.user.partner_id.id
        return bool(self.search([('partner_id', '=', partner_id), ('product_id', '=', product_id)]))


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def get_wishlist_products(self, limit=20):
        partner_id = self.env.user.partner_id.id
        wishlist_items = self.env['product.wishlist'].search([
            ('partner_id', '=', partner_id),
            ('active', '=', True)
        ], limit=limit, order='date_added desc')
        return wishlist_items.product_id


class ResPartner(models.Model):
    _inherit = 'res.partner'

    wishlist_ids = fields.One2many('product.wishlist', 'partner_id', string='Wishlist Items')
    wishlist_count = fields.Integer('Wishlist Count', compute='_compute_wishlist_count')

    @api.depends('wishlist_ids.active')
    def _compute_wishlist_count(self):
        for partner in self:
            partner.wishlist_count = len(partner.wishlist_ids.filtered('active'))