# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website
import logging

_logger = logging.getLogger(__name__)


class TechDreamWebsite(Website):
    """Enhanced website controller for TechDream theme"""

    # Basic routes that should work
    @http.route(['/shop/smartphones', '/shop/category/smartphones'], type='http', auth="public", website=True)
    def smartphones(self, **kw):
        """Smartphones category page"""
        return request.redirect('/shop')

    @http.route(['/shop/accessories', '/shop/category/accessories'], type='http', auth="public", website=True)
    def accessories(self, **kw):
        """Accessories category page"""
        return request.redirect('/shop')

    @http.route(['/shop/audio', '/shop/category/audio'], type='http', auth="public", website=True)
    def audio(self, **kw):
        """Audio category page"""
        return request.redirect('/shop')

    @http.route(['/shop/smartwatches', '/shop/category/smartwatches'], type='http', auth="public", website=True)
    def smartwatches(self, **kw):
        """Smartwatches category page"""
        return request.redirect('/shop')

    @http.route(['/shop/offers', '/shop/category/offers'], type='http', auth="public", website=True)
    def offers(self, **kw):
        """Special offers page"""
        return request.redirect('/shop')

    @http.route('/contact', type='http', auth="public", website=True)
    def contact_us(self, **kw):
        """Contact us page"""
        return request.redirect('/contactus')