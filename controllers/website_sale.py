# -*- coding: utf-8 -*-

from odoo import http, _
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

        # Add price filtering
        min_price = request.httprequest.args.get('min_price')
        max_price = request.httprequest.args.get('max_price')

        if min_price:
            try:
                domain.append(('list_price', '>=', float(min_price)))
            except (ValueError, TypeError):
                pass

        if max_price:
            try:
                domain.append(('list_price', '<=', float(max_price)))
            except (ValueError, TypeError):
                pass

        return domain

    @http.route()
    def shop(self, page=0, category=None, search='', min_price=0, max_price=0, ppg=False, **post):
        """Enhanced shop page"""

        # Call parent shop method
        response = super().shop(page=page, category=category, search=search, ppg=ppg, **post)

        # Get the values from the parent response
        if hasattr(response, 'qcontext'):
            values = response.qcontext

            # Add brands for filtering
            try:
                brands = request.env['product.brand'].sudo().search([])
                values['brands'] = brands
            except:
                values['brands'] = []

            # Add filter parameters for template
            values.update({
                'min_price': min_price,
                'max_price': max_price,
                'brand': post.get('brand', ''),
            })

            # Override template if we have our custom one
            try:
                request.env.ref('shasha.shop_page_template')
                response.template = 'shasha.shop_page_template'
            except:
                # Use default template if our custom one doesn't exist
                pass

        return response

    @http.route()
    def product(self, product, category='', search='', **kwargs):
        """Enhanced product page"""

        # Call parent product method
        response = super().product(product, category=category, search=search, **kwargs)

        if hasattr(response, 'qcontext'):
            values = response.qcontext

            # Add recently viewed
            try:
                request.env['product.recently.viewed'].sudo().add_product_view(product.id)
            except:
                pass

            # Check if in wishlist
            try:
                in_wishlist = False
                if not request.env.user._is_public():
                    wishlist_items = request.env['product.wishlist'].sudo().search([
                        ('partner_id', '=', request.env.user.partner_id.id),
                        ('product_id', 'in', product.product_variant_ids.ids)
                    ])
                    in_wishlist = bool(wishlist_items)
                values['in_wishlist'] = in_wishlist
            except:
                values['in_wishlist'] = False

            # Add inventory status
            try:
                values['inventory_status'] = {
                    'qty_available': sum(product.product_variant_ids.mapped('qty_available')),
                    'stock_status': 'in_stock' if any(v.qty_available > 0 for v in product.product_variant_ids) else 'out_of_stock'
                }
            except:
                values['inventory_status'] = {'qty_available': 0, 'stock_status': 'in_stock'}

            # Override template if we have our custom one
            try:
                request.env.ref('shasha.product_detail_template')
                response.template = 'shasha.product_detail_template'
            except:
                # Use default template if our custom one doesn't exist
                pass

        return response

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """Enhanced cart update"""

        # Call parent method
        response = super().cart_update(product_id=product_id, add_qty=add_qty, set_qty=set_qty, **kw)

        # Add success message if it's an AJAX request
        if request.httprequest.headers.get('Content-Type') == 'application/json':
            order = request.website.sale_get_order()
            return request.make_json_response({
                'success': True,
                'cart_quantity': int(sum(order.order_line.mapped('product_uom_qty'))),
                'amount_total': order.amount_total,
                'currency_symbol': order.currency_id.symbol,
            })

        return response