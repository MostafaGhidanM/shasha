# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website
import logging

_logger = logging.getLogger(__name__)


class TechDreamWebsite(Website):
    """Enhanced website controller for TechDream theme"""

    @http.route('/', type='http', auth="public", website=True, sitemap=True)
    def index(self, **kw):
        """Enhanced homepage with featured products and categories"""

        # Get featured products
        featured_products = request.env['product.template'].sudo().search([
            ('website_published', '=', True),
            ('sale_ok', '=', True),
        ], limit=8, order='website_sequence, create_date desc')

        # Get product categories
        categories = request.env['product.public.category'].sudo().search([
            ('parent_id', '=', False),
        ], limit=4, order='sequence, name')

        # Get latest products
        latest_products = request.env['product.template'].sudo().search([
            ('website_published', '=', True),
            ('sale_ok', '=', True),
        ], limit=4, order='create_date desc')

        values = {
            'featured_products': featured_products,
            'categories': categories,
            'latest_products': latest_products,
        }

        # Try to use custom homepage template, fallback to default
        try:
            request.env.ref('shasha.techdream_homepage_enhanced')
            return request.render('shasha.techdream_homepage_enhanced', values)
        except:
            # Use default homepage if custom template doesn't exist
            return super().index(**kw)