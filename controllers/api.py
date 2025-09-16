# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json


class ShashaAPI(http.Controller):

    @http.route('/api/products/featured', type='json', auth='public', website=True, methods=['GET'])
    def api_featured_products(self, limit=8, **kw):
        """API endpoint for featured products"""
        products = request.website.get_featured_products(limit=limit)
        return self._format_products(products)

    @http.route('/api/products/latest', type='json', auth='public', website=True, methods=['GET'])
    def api_latest_products(self, limit=12, **kw):
        """API endpoint for latest products"""
        products = request.website.get_latest_products(limit=limit)
        return self._format_products(products)

    @http.route('/api/products/bestsellers', type='json', auth='public', website=True, methods=['GET'])
    def api_best_sellers(self, limit=8, **kw):
        """API endpoint for best selling products"""
        products = request.website.get_best_sellers(limit=limit)
        return self._format_products(products)

    @http.route('/api/categories', type='json', auth='public', website=True, methods=['GET'])
    def api_categories(self, **kw):
        """API endpoint for categories"""
        categories = request.env['product.public.category'].search([
            ('website_published', '=', True),
        ])
        return [{
            'id': cat.id,
            'name': cat.name,
            'image': cat.image_1920,
            'product_count': request.env['product.template'].search_count([
                ('website_published', '=', True),
                ('public_categ_ids', 'child_of', cat.id)
            ]),
        } for cat in categories]

    @http.route('/api/brands', type='json', auth='public', website=True, methods=['GET'])
    def api_brands(self, **kw):
        """API endpoint for brands"""
        brands = request.env['product.brand'].search([
            ('website_published', '=', True),
            ('active', '=', True),
        ])
        return [{
            'id': brand.id,
            'name': brand.name,
            'image': brand.image,
            'product_count': brand.product_count,
        } for brand in brands]

    @http.route('/api/cart/summary', type='json', auth='public', website=True, methods=['GET'])
    def api_cart_summary(self, **kw):
        """API endpoint for cart summary"""
        return request.env['sale.order'].get_cart_summary()

    def _format_products(self, products):
        """Format products for API response"""
        result = []
        for product in products:
            combination_info = product._get_combination_info_variant()
            result.append({
                'id': product.id,
                'name': product.name,
                'description_sale': product.description_sale or '',
                'image': product.image_1920,
                'brand': product.brand_id.name if product.brand_id else '',
                'list_price': combination_info['list_price'],
                'price': combination_info['price'],
                'has_discounted_price': combination_info['has_discounted_price'],
                'currency_symbol': request.website.pricelist_id.currency_id.symbol,
                'rating': product.rating_avg if hasattr(product, 'rating_avg') else 0,
                'website_url': product.website_url,
                'is_featured': product.is_featured if hasattr(product, 'is_featured') else False,
                'badge_text': product.badge_text if hasattr(product, 'badge_text') else '',
                'badge_color': product.badge_color if hasattr(product, 'badge_color') else 'primary',
            })
        return result