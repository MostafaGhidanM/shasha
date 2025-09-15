# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Website(models.Model):
    _inherit = 'website'
    
    def get_featured_products(self, limit=8):
        """Get featured products for homepage"""
        return self.env['product.template'].search([
            ('website_published', '=', True),
            ('is_featured', '=', True),
            ('sale_ok', '=', True)
        ], limit=limit, order='website_sequence, name')
    
    def get_latest_products(self, limit=4):
        """Get latest products"""
        return self.env['product.template'].search([
            ('website_published', '=', True),
            ('sale_ok', '=', True)
        ], limit=limit, order='create_date desc')
    
    def get_sale_products(self, limit=4):
        """Get products on sale"""
        return self.env['product.template'].search([
            ('website_published', '=', True),
            ('sale_ok', '=', True),
            ('compare_list_price', '>', 0),
            ('list_price', '<', 'compare_list_price')
        ], limit=limit, order='discount_percentage desc')


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    category_icon = fields.Char(
        string='Category Icon',
        help='Font Awesome icon class (e.g., fas fa-mobile-alt)',
        default='fas fa-cube'
    )

    category_color = fields.Char(
        string='Category Color',
        help='Hex color code for category theme',
        default='#3498db'
    )

    is_featured = fields.Boolean(
        string='Featured Category',
        default=False,
        help='Display this category on homepage'
    )

    banner_image = fields.Binary(
        string='Banner Image',
        help='Category banner image'
    )

    description = fields.Html(
        string='Description',
        help='Category description'
    )

    product_count = fields.Integer(
        string='Product Count',
        compute='_compute_product_count',
        help='Number of products in this category'
    )

    @api.depends('product_tmpl_ids')
    def _compute_product_count(self):
        for category in self:
            # Count published products in this category
            category.product_count = self.env['product.template'].search_count([
                ('public_categ_ids', 'child_of', category.id),
                ('website_published', '=', True),
                ('sale_ok', '=', True)
            ])