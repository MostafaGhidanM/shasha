# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class TechDreamAPI(http.Controller):
    """API endpoints for AJAX functionality"""

    @http.route('/api/cart/add', type='json', auth="public", website=True)
    def cart_add(self, product_id, quantity=1, **kwargs):
        """Add product to cart via AJAX"""
        try:
            # Get or create order
            order = request.website.sale_get_order(force_create=True)

            # Get product
            product = request.env['product.product'].sudo().browse(int(product_id))
            if not product.exists():
                return {'error': 'Product not found'}

            # Add to cart
            order._cart_update(
                product_id=int(product_id),
                add_qty=float(quantity),
                **kwargs
            )

            # Return cart info
            return {
                'success': True,
                'cart_quantity': int(sum(order.order_line.mapped('product_uom_qty'))),
                'amount_total': order.amount_total,
                'currency_symbol': order.currency_id.symbol,
                'message': f'{product.name} added to cart'
            }

        except Exception as e:
            _logger.error(f"Cart add error: {str(e)}")
            return {'error': 'Failed to add to cart'}

    @http.route('/api/cart/update', type='json', auth="public", website=True)
    def cart_update(self, line_id, quantity):
        """Update cart line quantity"""
        try:
            order = request.website.sale_get_order()
            if not order:
                return {'error': 'No active order'}

            line = order.order_line.filtered(lambda l: l.id == int(line_id))
            if not line:
                return {'error': 'Order line not found'}

            quantity = float(quantity)
            if quantity <= 0:
                line.unlink()
            else:
                line.product_uom_qty = quantity

            return {
                'success': True,
                'cart_quantity': int(sum(order.order_line.mapped('product_uom_qty'))),
                'amount_total': order.amount_total,
                'line_total': line.price_subtotal if line.exists() else 0,
                'currency_symbol': order.currency_id.symbol,
            }

        except Exception as e:
            _logger.error(f"Cart update error: {str(e)}")
            return {'error': 'Failed to update cart'}

    @http.route('/api/cart/remove', type='json', auth="public", website=True)
    def cart_remove(self, line_id):
        """Remove line from cart"""
        try:
            order = request.website.sale_get_order()
            if not order:
                return {'error': 'No active order'}

            line = order.order_line.filtered(lambda l: l.id == int(line_id))
            if line:
                line.unlink()

            return {
                'success': True,
                'cart_quantity': int(sum(order.order_line.mapped('product_uom_qty'))),
                'amount_total': order.amount_total,
                'currency_symbol': order.currency_id.symbol,
            }

        except Exception as e:
            _logger.error(f"Cart remove error: {str(e)}")
            return {'error': 'Failed to remove from cart'}

    @http.route('/api/wishlist/toggle', type='json', auth="user", website=True)
    def wishlist_toggle(self, product_id):
        """Toggle product in wishlist"""
        try:
            product = request.env['product.product'].sudo().browse(int(product_id))
            if not product.exists():
                return {'error': 'Product not found'}

            partner = request.env.user.partner_id
            wishlist_item = request.env['product.wishlist'].sudo().search([
                ('partner_id', '=', partner.id),
                ('product_id', '=', product.id)
            ])

            if wishlist_item:
                wishlist_item.unlink()
                in_wishlist = False
                message = 'Removed from wishlist'
            else:
                request.env['product.wishlist'].sudo().create({
                    'partner_id': partner.id,
                    'product_id': product.id,
                })
                in_wishlist = True
                message = 'Added to wishlist'

            return {
                'success': True,
                'in_wishlist': in_wishlist,
                'message': message
            }

        except Exception as e:
            _logger.error(f"Wishlist toggle error: {str(e)}")
            return {'error': 'Please login to use wishlist'}

    @http.route('/api/products/search', type='json', auth="public", website=True)
    def search_products(self, query='', limit=10):
        """Search products for autocomplete"""
        try:
            domain = [
                ('website_published', '=', True),
                ('sale_ok', '=', True),
                '|',
                ('name', 'ilike', query),
                ('description_sale', 'ilike', query)
            ]

            products = request.env['product.template'].sudo().search(domain, limit=limit)

            result = []
            for product in products:
                result.append({
                    'id': product.id,
                    'name': product.name,
                    'price': product.list_price,
                    'currency_symbol': request.website.currency_id.symbol,
                    'image_url': f'/web/image/product.template/{product.id}/image_1024',
                    'url': f'/shop/product/{product.id}',
                })

            return {'products': result}

        except Exception as e:
            _logger.error(f"Product search error: {str(e)}")
            return {'products': []}

    @http.route('/api/inventory/check', type='json', auth="public", website=True)
    def check_inventory(self, product_id, quantity=1):
        """Check product inventory"""
        try:
            product = request.env['product.template'].sudo().browse(int(product_id))
            if not product.exists():
                return {'error': 'Product not found'}

            # Get total available quantity
            total_qty = sum(product.product_variant_ids.mapped('qty_available'))
            available = total_qty >= float(quantity)

            stock_status = 'in_stock'
            if total_qty <= 0:
                stock_status = 'out_of_stock'
            elif total_qty <= 10:  # Low stock threshold
                stock_status = 'low_stock'

            return {
                'success': True,
                'available': available,
                'qty_available': total_qty,
                'stock_status': stock_status,
                'message': 'Available' if available else f'Only {total_qty} available'
            }

        except Exception as e:
            _logger.error(f"Inventory check error: {str(e)}")
            return {'error': 'Could not check inventory'}