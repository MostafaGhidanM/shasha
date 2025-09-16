# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def get_featured_products(self, limit=8):
        return self.env['product.template'].search([
            ('website_published', '=', True),
            ('is_featured', '=', True),
            ('sale_ok', '=', True),
        ], limit=limit, order='create_date desc')

    @api.model
    def get_latest_products(self, limit=12):
        return self.env['product.template'].search([
            ('website_published', '=', True),
            ('sale_ok', '=', True),
        ], limit=limit, order='create_date desc')

    @api.model
    def get_best_sellers(self, limit=8):
        # Get products with highest sales
        query = """
            SELECT pt.id, SUM(sol.product_uom_qty) as total_sold
            FROM product_template pt
            JOIN product_product pp ON pp.product_tmpl_id = pt.id
            JOIN sale_order_line sol ON sol.product_id = pp.id
            JOIN sale_order so ON so.id = sol.order_id
            WHERE pt.website_published = true
            AND pt.sale_ok = true
            AND so.state IN ('sale', 'done')
            GROUP BY pt.id
            ORDER BY total_sold DESC
            LIMIT %s
        """
        self.env.cr.execute(query, (limit,))
        product_ids = [row[0] for row in self.env.cr.fetchall()]
        return self.env['product.template'].browse(product_ids)

    @api.model
    def get_categories_with_products(self):
        categories = self.env['product.public.category'].search([
            ('website_published', '=', True),
            ('parent_id', '=', False),
        ])
        result = []
        for category in categories:
            product_count = self.env['product.template'].search_count([
                ('website_published', '=', True),
                ('public_categ_ids', 'child_of', category.id)
            ])
            if product_count > 0:
                result.append({
                    'category': category,
                    'product_count': product_count,
                })
        return result

    @api.model
    def get_brands_with_products(self):
        brands = self.env['product.brand'].search([
            ('website_published', '=', True),
            ('active', '=', True),
        ])
        result = []
        for brand in brands:
            product_count = self.env['product.template'].search_count([
                ('website_published', '=', True),
                ('brand_id', '=', brand.id)
            ])
            if product_count > 0:
                result.append({
                    'brand': brand,
                    'product_count': product_count,
                })
        return result