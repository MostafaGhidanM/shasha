# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json


class ShashaShop(http.Controller):

    @http.route('/shop/cart/update_json', type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True, **kw):
        """Update cart via JSON (AJAX)"""
        order = request.website.sale_get_order(force_create=True)
        if order.state != 'draft':
            order = request.website.sale_get_order(force_create=True)

        product = request.env['product.product'].browse(int(product_id))

        if add_qty is not None:
            add_qty = float(add_qty)

        if set_qty is not None:
            set_qty = float(set_qty)

        if line_id:
            order_line = order.order_line.browse(int(line_id))
            if set_qty is not None:
                order_line.product_uom_qty = set_qty
            elif add_qty is not None:
                order_line.product_uom_qty += add_qty
        else:
            order._cart_update(
                product_id=int(product_id),
                add_qty=add_qty or 1,
                set_qty=set_qty,
                **kw
            )

        # Return cart summary
        cart_quantity = sum(order.order_line.mapped('product_uom_qty'))
        return {
            'cart_quantity': cart_quantity,
            'amount_total': order.amount_total,
            'currency_symbol': order.currency_id.symbol,
        }

    @http.route('/shop/wishlist/toggle', type='json', auth='user', methods=['POST'], website=True)
    def toggle_wishlist(self, product_id, **kw):
        """Toggle product in/out of wishlist"""
        result = request.env['product.wishlist'].toggle_wishlist(int(product_id))
        return result

    @http.route('/shop/wishlist', type='http', auth='user', website=True)
    def wishlist(self, **kw):
        """User's wishlist page"""
        wishlist_products = request.env['product.template'].get_wishlist_products()
        return request.render('shasha.wishlist_page', {
            'products': wishlist_products,
        })

    @http.route('/shop/compare', type='http', auth='public', website=True)
    def compare(self, **kw):
        """Product comparison page"""
        compare_list = request.session.get('comparison_list', [])
        products = request.env['product.template'].browse(compare_list)

        # Get all attributes for comparison
        attributes = []
        if products:
            all_attributes = products.mapped('attribute_line_ids.attribute_id')
            for attr in all_attributes:
                attr_values = {}
                for product in products:
                    product_attr_values = product.attribute_line_ids.filtered(
                        lambda l: l.attribute_id.id == attr.id
                    ).value_ids
                    attr_values[product.id] = product_attr_values.mapped('name')
                attributes.append({
                    'attribute': attr,
                    'values': attr_values,
                })

        return request.render('shasha.compare_page', {
            'products': products,
            'attributes': attributes,
        })

    @http.route('/shop/compare/add/<int:product_id>', type='json', auth='public', website=True)
    def add_to_compare(self, product_id, **kw):
        """Add product to comparison"""
        compare_list = request.session.get('comparison_list', [])
        if product_id not in compare_list and len(compare_list) < 4:
            compare_list.append(product_id)
            request.session['comparison_list'] = compare_list
            return {'success': True, 'message': 'Product added to comparison'}
        elif product_id in compare_list:
            return {'success': False, 'message': 'Product already in comparison'}
        else:
            return {'success': False, 'message': 'Maximum 4 products can be compared'}

    @http.route('/shop/compare/remove/<int:product_id>', type='json', auth='public', website=True)
    def remove_from_compare(self, product_id, **kw):
        """Remove product from comparison"""
        compare_list = request.session.get('comparison_list', [])
        if product_id in compare_list:
            compare_list.remove(product_id)
            request.session['comparison_list'] = compare_list
            return {'success': True, 'message': 'Product removed from comparison'}
        return {'success': False, 'message': 'Product not in comparison'}

    @http.route('/shop/compare/clear', type='json', auth='public', website=True)
    def clear_compare(self, **kw):
        """Clear all products from comparison"""
        request.session['comparison_list'] = []
        return {'success': True, 'message': 'Comparison list cleared'}

    @http.route('/shop/product/quick_view/<int:product_id>', type='json', auth='public', website=True)
    def product_quick_view(self, product_id, **kw):
        """Get product details for quick view modal"""
        product = request.env['product.template'].browse(product_id)
        if not product.exists() or not product.website_published:
            return {'error': 'Product not found'}

        pricelist = request.website.pricelist_id
        combination_info = product._get_combination_info_variant()

        return {
            'product': {
                'id': product.id,
                'name': product.name,
                'description_sale': product.description_sale,
                'image_1920': product.image_1920,
                'brand': product.brand_id.name if product.brand_id else '',
                'list_price': combination_info['list_price'],
                'price': combination_info['price'],
                'has_discounted_price': combination_info['has_discounted_price'],
                'currency': pricelist.currency_id.symbol,
                'rating': product.rating_avg,
                'rating_count': product.rating_count,
                'website_url': product.website_url,
            }
        }

    @http.route('/shop/get_filters', type='json', auth='public', website=True)
    def get_shop_filters(self, category=None, search='', **kw):
        """Get available filters for shop"""
        domain = [('website_published', '=', True)]

        if search:
            domain += ['|', ('name', 'ilike', search), ('description_sale', 'ilike', search)]

        if category:
            domain += [('public_categ_ids', 'child_of', int(category))]

        products = request.env['product.template'].search(domain)

        # Get price range
        prices = products.mapped('list_price')
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        # Get available brands
        brands = products.mapped('brand_id').filtered('website_published')

        # Get available attributes
        attributes = request.env['product.attribute'].search([
            ('attribute_line_ids.product_tmpl_id', 'in', products.ids)
        ])

        return {
            'price_range': {'min': min_price, 'max': max_price},
            'brands': [{'id': b.id, 'name': b.name} for b in brands],
            'attributes': [{
                'id': attr.id,
                'name': attr.name,
                'values': [{
                    'id': val.id,
                    'name': val.name
                } for val in attr.value_ids]
            } for attr in attributes],
        }