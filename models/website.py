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
        # Get products with highest sales - use ORM instead of raw SQL
        products = self.env['product.template'].search([
            ('website_published', '=', True),
            ('sale_ok', '=', True),
        ])

        # Calculate sales for each product
        product_sales = []
        for product in products:
            sales_count = self.env['sale.order.line'].search_count([
                ('product_template_id', '=', product.id),
                ('order_id.state', 'in', ['sale', 'done'])
            ])
            if sales_count > 0:
                product_sales.append((product, sales_count))

        # Sort by sales count and return top products
        product_sales.sort(key=lambda x: x[1], reverse=True)
        return self.env['product.template'].browse([p[0].id for p in product_sales[:limit]])

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