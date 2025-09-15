# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging

_logger = logging.getLogger(__name__)


class TechDreamWebsiteSale(WebsiteSale):
    """Enhanced WebsiteSale controller for TechDream theme"""

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        """Override to add custom search logic"""
        domain = super()._get_search_domain(search, category, attrib_values, search_in_description)

        # Add brand filtering if brand parameter exists
        brand = request.httprequest.args.get('brand')
        if brand:
            try:
                brand_id = int(brand)
                domain.append(('brand_id', '=', brand_id))
            except (ValueError, TypeError):
                pass

        return domain

    @http.route()
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        """Enhanced shop route with brand support"""
        # Add brands to context for template
        result = super().shop(page=page, category=category, search=search,
                            min_price=min_price, max_price=max_price, ppg=ppg, **post)

        if hasattr(result, 'qcontext'):
            # Add available brands to template context
            brands = request.env['product.brand'].sudo().search([
                ('website_published', '=', True),
                ('product_count', '>', 0)
            ], limit=20, order='name')
            result.qcontext['brands'] = brands

        return result