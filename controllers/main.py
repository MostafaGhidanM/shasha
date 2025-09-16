# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class ShashaMain(http.Controller):

    @http.route('/', type='http', auth='public', website=True)
    def index(self, **kw):
        """Enhanced homepage with product sections"""
        website = request.website
        values = {
            'featured_products': website.get_featured_products(limit=8),
            'latest_products': website.get_latest_products(limit=12),
            'best_sellers': website.get_best_sellers(limit=8),
            'categories': website.get_categories_with_products()[:6],
            'brands': website.get_brands_with_products()[:8],
        }
        return request.render('shasha.homepage', values)

    @http.route('/about', type='http', auth='public', website=True, sitemap=True)
    def about(self, **kw):
        """About us page"""
        return request.render('shasha.about_page', {})

    @http.route('/contact', type='http', auth='public', website=True, sitemap=True)
    def contact(self, **kw):
        """Contact page"""
        return request.render('shasha.contact_page', {})

    @http.route('/brands', type='http', auth='public', website=True, sitemap=True)
    def brands(self, **kw):
        """Brands listing page"""
        brands = request.env['product.brand'].search([
            ('active', '=', True),
        ])
        return request.render('shasha.brands_page', {'brands': brands})

    @http.route('/brand/<model("product.brand"):brand>', type='http', auth='public', website=True, sitemap=True)
    def brand_products(self, brand, **kw):
        """Products by brand"""
        products = request.env['product.template'].search([
            ('website_published', '=', True),
            ('brand_id', '=', brand.id),
        ])
        return request.render('website_sale.products', {
            'products': products,
            'search': f"Brand: {brand.name}",
        })


class ShashaWebsiteSale(WebsiteSale):
    pass