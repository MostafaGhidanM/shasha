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

    # Remove custom shop route override to avoid template conflicts
    # Use Odoo's default shop functionality