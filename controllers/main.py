# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import Website
from odoo.addons.portal.controllers.portal import CustomerPortal
import json
import logging

_logger = logging.getLogger(__name__)


class TechDreamWebsite(Website):
    """Main website controller for TechDream theme"""

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        """Enhanced homepage with featured products and categories"""
        
        # Get featured products
        featured_products = request.env['product.template'].sudo().search([
            ('website_published', '=', True),
            ('is_published', '=', True),
        ], limit=8, order='create_date desc')
        
        # Get product categories - use parent_id filter instead of website_published
        categories = request.env['product.public.category'].sudo().search([
            ('parent_id', '=', False),
        ], limit=4)
        
        # Get latest products
        latest_products = request.env['product.template'].sudo().search([
            ('website_published', '=', True),
        ], limit=4, order='create_date desc')
        
        # Get special offers
        special_offers = request.env['product.template'].sudo().search([
            ('website_published', '=', True),
            ('sale_ok', '=', True),
            '|',
            ('list_price', '>', 0),
            ('compare_list_price', '>', 0)
        ], limit=4)
        
        values = {
            'featured_products': featured_products,
            'categories': categories,
            'latest_products': latest_products,
            'special_offers': special_offers,
        }
        
        return request.render('shasha.techdream_homepage_enhanced', values)


class TechDreamShop(WebsiteSale):
    """Enhanced shop controller with advanced filtering"""

    @http.route(['/shop', '/shop/page/<int:page>'], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', min_price=0, max_price=0, brand=None, **post):
        """Enhanced shop page with filters"""
        
        # Build domain for product search
        domain = [('website_published', '=', True)]
        
        # Category filter
        if category:
            try:
                category_obj = request.env['product.public.category'].sudo().browse(int(category))
                if category_obj.exists():
                    domain.append(('public_categ_ids', 'child_of', category_obj.id))
            except ValueError:
                pass
        
        # Search filter
        if search:
            domain.extend(['|', 
                          ('name', 'ilike', search),
                          ('description_sale', 'ilike', search)])
        
        # Price filter
        if min_price:
            domain.append(('list_price', '>=', float(min_price)))
        if max_price:
            domain.append(('list_price', '<=', float(max_price)))
        
        # Brand filter (assuming you have a brand field)
        if brand:
            domain.append(('brand_id', '=', int(brand)))
        
        # Get sorting
        order = post.get('order', 'website_sequence desc')
        
        # Products per page
        ppg = 12
        
        # Get total count
        total_count = request.env['product.template'].sudo().search_count(domain)
        
        # Calculate pagination
        pager = request.website.pager(
            url='/shop',
            url_args=post,
            total=total_count,
            page=page,
            step=ppg
        )
        
        # Get products
        products = request.env['product.template'].sudo().search(
            domain,
            limit=ppg,
            offset=pager['offset'],
            order=order
        )
        
        # Get categories for sidebar - removed website_published filter
        categories = request.env['product.public.category'].sudo().search([
            ('parent_id', '=', False),
        ])
        
        # Get brands for filter
        brands = request.env['product.brand'].sudo().search([])
        
        values = {
            'products': products,
            'categories': categories,
            'brands': brands,
            'pager': pager,
            'search': search,
            'category': category,
            'min_price': min_price,
            'max_price': max_price,
            'brand': brand,
            'order': order,
            'bins': lambda *args: [products[i:i+4] for i in range(0, len(products), 4)],
        }
        
        return request.render('shasha.shop_page_template', values)

    @http.route(['/shop/category/<model("product.public.category"):category>'], type='http', auth="public", website=True)
    def category(self, category, **post):
        """Category page"""
        return self.shop(category=category.id, **post)

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        """Enhanced product detail page"""

        # Add to recently viewed
        request.env['product.recently.viewed'].sudo().add_product_view(product.id)

        # Get product variants
        variants = product.product_variant_ids.filtered(lambda v: v.active)

        # Get related products
        related_products = product.get_similar_products(limit=4)
        if not related_products:
            related_products = request.env['product.template'].sudo().search([
                ('website_published', '=', True),
                ('public_categ_ids', 'in', product.public_categ_ids.ids),
                ('id', '!=', product.id)
            ], limit=4)

        # Get product reviews (if review module is installed)
        reviews = []
        if hasattr(product, 'website_message_ids'):
            reviews = product.website_message_ids.filtered(
                lambda m: m.message_type == 'comment' and not m.parent_id
            )[:5]

        # Get product specifications
        specifications = []
        if hasattr(product, 'product_template_attribute_value_ids'):
            specifications = product.product_template_attribute_value_ids

        # Check if in wishlist
        in_wishlist = False
        if not request.env.user._is_public():
            in_wishlist = request.env['product.wishlist'].sudo().is_in_wishlist(
                product.product_variant_id.id,
                request.env.user.partner_id.id
            )

        # Get inventory status
        inventory_status = product.get_inventory_status()

        # Get cross-sell and up-sell products
        cross_sell_products = product.cross_sell_product_ids.filtered('website_published')[:4]
        up_sell_products = product.up_sell_product_ids.filtered('website_published')[:4]

        values = {
            'product': product,
            'variants': variants,
            'related_products': related_products,
            'cross_sell_products': cross_sell_products,
            'up_sell_products': up_sell_products,
            'reviews': reviews,
            'specifications': specifications,
            'category': category,
            'search': search,
            'in_wishlist': in_wishlist,
            'inventory_status': inventory_status,
        }

        return request.render('shasha.product_detail_template', values)

    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, access_token=None, revive='', **post):
        """Enhanced cart page"""
        order = request.website.sale_get_order()
        
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
        
        values = {
            'website_sale_order': order,
            'compute_currency': lambda price: request.env['product.template']._get_combination_info_variant()['price'],
            'suggested_products': [],
        }
        
        if order:
            # Get suggested products based on cart items
            categories = order.order_line.mapped('product_id.public_categ_ids')
            suggested_products = request.env['product.template'].sudo().search([
                ('website_published', '=', True),
                ('public_categ_ids', 'in', categories.ids),
                ('id', 'not in', order.order_line.mapped('product_id.product_tmpl_id.id'))
            ], limit=4)
            values['suggested_products'] = suggested_products
        
        return request.render('shasha.cart_page_template', values)

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        """Enhanced checkout page"""
        order = request.website.sale_get_order()
        
        if not order or not order.order_line:
            return request.redirect('/shop')
        
        # Get shipping methods
        shipping_methods = []
        if 'delivery.carrier' in request.env:
            shipping_methods = request.env['delivery.carrier'].sudo().search([
                ('active', '=', True)
            ])
        
        # Get payment methods
        payment_methods = []
        if 'payment.provider' in request.env:
            payment_methods = request.env['payment.provider'].sudo().search([
                ('state', 'in', ['enabled', 'test'])
            ])
        
        values = {
            'website_sale_order': order,
            'shipping_methods': shipping_methods,
            'payment_methods': payment_methods,
            'countries': request.env['res.country'].sudo().search([]),
            'states': request.env['res.country.state'].sudo().search([]),
        }
        
        return request.render('shasha.checkout_page_template', values)


class TechDreamContact(http.Controller):
    """Contact page controller"""

    @http.route(['/contact'], type='http', auth="public", website=True)
    def contact(self, **kwargs):
        """Contact page"""
        values = {
            'success': kwargs.get('success', False),
            'error': kwargs.get('error', False),
        }
        return request.render('shasha.contact_page_template', values)

    @http.route(['/contact/submit'], type='http', auth="public", website=True, csrf=False)
    def contact_submit(self, **post):
        """Handle contact form submission"""
        try:
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'subject', 'message']
            for field in required_fields:
                if not post.get(field):
                    return request.redirect('/contact?error=missing_fields')
            
            # Send email
            mail_values = {
                'subject': f"Contact Form: {post.get('subject')}",
                'body_html': f"""
                    <p><strong>Name:</strong> {post.get('first_name')} {post.get('last_name')}</p>
                    <p><strong>Email:</strong> {post.get('email')}</p>
                    <p><strong>Phone:</strong> {post.get('phone', 'Not provided')}</p>
                    <p><strong>Subject:</strong> {post.get('subject')}</p>
                    <p><strong>Message:</strong></p>
                    <p>{post.get('message')}</p>
                """,
                'email_to': 'info@techdream.ae',
                'email_from': post.get('email'),
            }
            request.env['mail.mail'].sudo().create(mail_values).send()
            
            return request.redirect('/contact?success=1')
            
        except Exception as e:
            _logger.error(f"Contact form submission error: {str(e)}")
            return request.redirect('/contact?error=1')


class TechDreamAPI(http.Controller):
    """API endpoints for AJAX requests"""

    @http.route(['/api/products/search'], type='json', auth="public", website=True)
    def search_products(self, query='', limit=10):
        """AJAX product search"""
        domain = [
            ('website_published', '=', True),
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
                'currency': request.website.currency_id.symbol,
                'image_url': f'/web/image/product.template/{product.id}/image_1024',
                'url': f'/shop/product/{product.id}',
            })
        
        return {'products': result}

    @http.route(['/api/cart/add'], type='json', auth="public", website=True)
    def cart_add_product(self, product_id, quantity=1, **kwargs):
        """Add product to cart via AJAX"""
        try:
            order = request.website.sale_get_order(force_create=True)
            product = request.env['product.template'].sudo().browse(product_id)
            
            if not product.exists():
                return {'error': 'Product not found'}
            
            # Add to cart
            order._cart_update(
                product_id=product.product_variant_id.id,
                add_qty=quantity,
                **kwargs
            )
            
            # Return cart info
            return {
                'success': True,
                'cart_quantity': sum(order.order_line.mapped('product_uom_qty')),
                'cart_total': order.amount_total,
                'currency': order.currency_id.symbol,
            }
            
        except Exception as e:
            _logger.error(f"Cart add error: {str(e)}")
            return {'error': str(e)}

    @http.route(['/api/cart/update'], type='json', auth="public", website=True)
    def cart_update_quantity(self, line_id, quantity):
        """Update cart line quantity via AJAX"""
        try:
            order = request.website.sale_get_order()
            if not order:
                return {'error': 'No active order'}
            
            line = order.order_line.filtered(lambda l: l.id == line_id)
            if not line:
                return {'error': 'Order line not found'}
            
            if quantity <= 0:
                line.unlink()
            else:
                line.product_uom_qty = quantity
            
            return {
                'success': True,
                'cart_quantity': sum(order.order_line.mapped('product_uom_qty')),
                'cart_total': order.amount_total,
                'line_total': line.price_subtotal if line.exists() else 0,
                'currency': order.currency_id.symbol,
            }
            
        except Exception as e:
            _logger.error(f"Cart update error: {str(e)}")
            return {'error': str(e)}

    @http.route(['/api/cart/remove'], type='json', auth="public", website=True)
    def cart_remove_line(self, line_id):
        """Remove cart line via AJAX"""
        try:
            order = request.website.sale_get_order()
            if not order:
                return {'error': 'No active order'}

            line = order.order_line.filtered(lambda l: l.id == line_id)
            if line:
                line.unlink()

            return {
                'success': True,
                'cart_quantity': sum(order.order_line.mapped('product_uom_qty')),
                'cart_total': order.amount_total,
                'currency': order.currency_id.symbol,
            }

        except Exception as e:
            _logger.error(f"Cart remove error: {str(e)}")
            return {'error': str(e)}

    @http.route(['/api/cart/estimate_shipping'], type='json', auth="public", website=True)
    def estimate_shipping(self, country_id, state_id=None):
        """Estimate shipping costs"""
        try:
            order = request.website.sale_get_order()
            if not order:
                return {'error': 'No active order'}

            # Get available carriers
            carriers = request.env['delivery.carrier'].sudo().search([
                ('website_published', '=', True)
            ])

            shipping_options = []
            for carrier in carriers:
                # Calculate shipping cost (simplified)
                cost = carrier.fixed_price or 0.0
                shipping_options.append({
                    'id': carrier.id,
                    'name': carrier.name,
                    'cost': cost,
                    'currency': order.currency_id.symbol,
                })

            return {
                'success': True,
                'shipping_options': shipping_options
            }

        except Exception as e:
            _logger.error(f"Shipping estimation error: {str(e)}")
            return {'error': str(e)}

    @http.route(['/api/wishlist/toggle'], type='json', auth="public", website=True)
    def wishlist_toggle(self, product_id):
        """Toggle product in wishlist"""
        if not request.env.user._is_public():
            try:
                product = request.env['product.template'].sudo().browse(product_id)
                if not product.exists():
                    return {'error': 'Product not found'}

                in_wishlist = request.env['product.wishlist'].sudo().toggle_product(
                    product.product_variant_id.id,
                    request.env.user.partner_id.id
                )

                return {
                    'success': True,
                    'in_wishlist': in_wishlist,
                }

            except Exception as e:
                _logger.error(f"Wishlist toggle error: {str(e)}")
                return {'error': str(e)}
        else:
            return {'error': 'Login required'}


class TechDreamAccount(CustomerPortal):
    """Enhanced customer account pages"""

    @http.route(['/my/account'], type='http', auth="user", website=True)
    def account(self, redirect=None, **post):
        """Enhanced account page"""
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        
        # Get recent orders
        orders = request.env['sale.order'].sudo().search([
            ('partner_id', '=', partner.id),
            ('state', 'in', ['sale', 'done'])
        ], limit=5, order='date_order desc')
        
        # Get wishlist items
        wishlist_items = []
        if 'product.wishlist' in request.env:
            wishlist_items = request.env['product.wishlist'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
        
        # Get recently viewed products
        recently_viewed = partner.get_recently_viewed_products(limit=8)

        values.update({
            'partner': partner,
            'recent_orders': orders,
            'wishlist_items': wishlist_items,
            'recently_viewed': recently_viewed,
            'page_name': 'account',
        })
        
        response = request.render("portal.portal_my_home", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


class TechDreamBlog(http.Controller):
    """Blog/News controller for tech news and reviews"""

    @http.route(['/blog', '/blog/page/<int:page>'], type='http', auth="public", website=True)
    def blog(self, page=0, **kwargs):
        """Blog listing page"""
        # Redirect to shop if blog module is not available
        return request.redirect('/shop')

        if False and 'blog.blog' in request.env:
            try:
                blogs = request.env['blog.blog'].sudo().search([
                    ('website_published', '=', True)
                ])
            except:
                # Fallback if website_published doesn't exist
                blogs = request.env['blog.blog'].sudo().search([])
            
            if blogs:
                blog = blogs[0]  # Get first blog
                
                domain = [('blog_id', '=', blog.id)]
                try:
                    domain.append(('website_published', '=', True))
                except:
                    # website_published might not exist for blog.post
                    domain.append(('active', '=', True))
                
                total = request.env['blog.post'].sudo().search_count(domain)
                page_detail = request.website.pager(
                    url='/blog',
                    total=total,
                    page=page,
                    step=5,
                    scope=7,
                    url_args=kwargs
                )
                
                posts = request.env['blog.post'].sudo().search(
                    domain,
                    limit=5,
                    offset=page_detail['offset'],
                    order='published_date desc'
                )
                
                values = {
                    'blog': blog,
                    'posts': posts,
                    'pager': page_detail,
                }
                
                return request.render('website_blog.blog_post_short', values)
        
        # Fallback if blog is not installed
        return request.redirect('/shop')


class TechDreamComparison(http.Controller):
    """Product comparison controller"""

    @http.route(['/shop/compare'], type='http', auth="public", website=True)
    def compare_products(self, **kwargs):
        """Product comparison page"""
        comparison = request.env['product.comparison'].sudo().get_comparison_for_user()

        if not comparison or not comparison.product_ids:
            return request.render('shasha.compare_empty_template')

        # Get comparison attributes
        attributes = comparison.get_comparison_attributes()

        values = {
            'comparison': comparison,
            'products': comparison.product_ids,
            'attributes': attributes,
        }

        return request.render('shasha.compare_products_template', values)

    @http.route(['/api/compare/add'], type='json', auth="public", website=True)
    def add_to_comparison(self, product_id):
        """Add product to comparison"""
        try:
            comparison = request.env['product.comparison'].sudo().get_comparison_for_user()

            if len(comparison.product_ids) >= 4:
                return {'error': 'Maximum 4 products can be compared'}

            success = comparison.add_product(product_id)

            return {
                'success': success,
                'count': len(comparison.product_ids),
                'message': 'Product added to comparison' if success else 'Product already in comparison'
            }

        except Exception as e:
            _logger.error(f"Comparison add error: {str(e)}")
            return {'error': str(e)}

    @http.route(['/api/compare/remove'], type='json', auth="public", website=True)
    def remove_from_comparison(self, product_id):
        """Remove product from comparison"""
        try:
            comparison = request.env['product.comparison'].sudo().get_comparison_for_user()
            success = comparison.remove_product(product_id)

            return {
                'success': success,
                'count': len(comparison.product_ids),
                'message': 'Product removed from comparison'
            }

        except Exception as e:
            _logger.error(f"Comparison remove error: {str(e)}")
            return {'error': str(e)}

    @http.route(['/api/compare/clear'], type='json', auth="public", website=True)
    def clear_comparison(self):
        """Clear all products from comparison"""
        try:
            comparison = request.env['product.comparison'].sudo().get_comparison_for_user()
            comparison.product_ids = [(5, 0, 0)]  # Remove all

            return {
                'success': True,
                'message': 'Comparison cleared'
            }

        except Exception as e:
            _logger.error(f"Comparison clear error: {str(e)}")
            return {'error': str(e)}


class TechDreamWishlist(http.Controller):
    """Wishlist controller"""

    @http.route(['/my/wishlist'], type='http', auth="user", website=True)
    def wishlist(self, **kwargs):
        """Customer wishlist page"""
        partner = request.env.user.partner_id
        wishlist_items = partner.get_customer_wishlist()

        values = {
            'wishlist_items': wishlist_items,
            'partner': partner,
        }

        return request.render('shasha.wishlist_template', values)

    @http.route(['/api/wishlist/move_to_cart'], type='json', auth="user", website=True)
    def move_to_cart(self, product_id, quantity=1):
        """Move product from wishlist to cart"""
        try:
            # Add to cart
            order = request.website.sale_get_order(force_create=True)
            order._cart_update(
                product_id=product_id,
                add_qty=quantity
            )

            # Remove from wishlist
            request.env['product.wishlist'].sudo().toggle_product(
                product_id,
                request.env.user.partner_id.id
            )

            return {
                'success': True,
                'message': 'Product moved to cart'
            }

        except Exception as e:
            _logger.error(f"Move to cart error: {str(e)}")
            return {'error': str(e)}


class TechDreamUtility(http.Controller):
    """Utility routes and helpers"""

    @http.route(['/sitemap.xml'], type='http', auth="public", website=True)
    def sitemap_xml_index(self):
        """Generate sitemap"""
        current_website = request.env['website'].get_current_website()
        Attachment = request.env['ir.attachment']
        View = request.env['ir.ui.view']
        mimetype = 'application/xml;charset=utf-8'
        content = None

        def create_sitemap(url, content):
            return Attachment.create({
                'datas': content,
                'mimetype': mimetype,
                'type': 'binary',
                'name': url,
                'url': url,
            })

        # Check if sitemap already exists
        sitemap_ira = Attachment.search([('url', '=', '/sitemap.xml'), ('website_id', '=', current_website.id)], limit=1)
        
        if sitemap_ira:
            content = sitemap_ira.datas
        else:
            # Generate sitemap content
            pages = [
                '/',
                '/shop',
                '/contact',
                '/blog',
            ]
            
            # Add product pages
            products = request.env['product.template'].sudo().search([
                ('website_published', '=', True)
            ])
            for product in products:
                pages.append(f'/shop/product/{product.id}')
            
            # Add category pages - removed website_published filter
            categories = request.env['product.public.category'].sudo().search([])
            for category in categories:
                pages.append(f'/shop/category/{category.id}')
            
            # Generate XML
            xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
            xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            
            for page in pages:
                xml_content += f'  <url>\n'
                xml_content += f'    <loc>{base_url}{page}</loc>\n'
                xml_content += f'    <changefreq>weekly</changefreq>\n'
                xml_content += f'    <priority>0.8</priority>\n'
                xml_content += f'  </url>\n'
            
            xml_content += '</urlset>'
            
            content = xml_content.encode('utf-8')
            sitemap_ira = create_sitemap('/sitemap.xml', content)

        return request.make_response(content, [('Content-Type', mimetype)])

    @http.route(['/robots.txt'], type='http', auth="public", website=True)
    def robots_txt(self):
        """Generate robots.txt"""
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        
        content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /web/
Disallow: /website/
Disallow: /shop/cart
Disallow: /shop/checkout

Sitemap: {base_url}/sitemap.xml
"""
        
        return request.make_response(content, [('Content-Type', 'text/plain')])

    @http.route(['/manifest.json'], type='http', auth="public", website=True)
    def manifest_json(self):
        """PWA manifest"""
        manifest = {
            "name": "TechDream Mobile",
            "short_name": "TechDream",
            "description": "Premium smartphones and accessories in UAE",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#2c3e50",
            "theme_color": "#3498db",
            "icons": [
                {
                    "src": "/shasha/static/src/img/icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/shasha/static/src/img/icon-512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ]
        }
        
        return request.make_response(
            json.dumps(manifest),
            [('Content-Type', 'application/json')]
        )

    @http.route(['/api/inventory/check'], type='json', auth="public", website=True)
    def check_inventory(self, product_id, quantity=1):
        """Check product inventory availability"""
        try:
            product = request.env['product.template'].sudo().browse(product_id)
            if not product.exists():
                return {'error': 'Product not found'}

            inventory_status = product.get_inventory_status()
            available = inventory_status['qty_available'] >= quantity

            return {
                'success': True,
                'available': available,
                'qty_available': inventory_status['qty_available'],
                'stock_status': inventory_status['stock_status'],
                'message': 'Available' if available else f'Only {inventory_status["qty_available"]} available'
            }

        except Exception as e:
            _logger.error(f"Inventory check error: {str(e)}")
            return {'error': str(e)}

    @http.route(['/api/products/filter'], type='json', auth="public", website=True)
    def filter_products(self, filters=None, page=1, limit=12):
        """Advanced product filtering API"""
        try:
            domain = [('website_published', '=', True)]

            if filters:
                # Category filter
                if filters.get('category_ids'):
                    domain.append(('public_categ_ids', 'in', filters['category_ids']))

                # Brand filter
                if filters.get('brand_ids'):
                    domain.append(('brand_id', 'in', filters['brand_ids']))

                # Price range
                if filters.get('min_price'):
                    domain.append(('list_price', '>=', filters['min_price']))
                if filters.get('max_price'):
                    domain.append(('list_price', '<=', filters['max_price']))

                # Stock status
                if filters.get('in_stock_only'):
                    domain.append(('stock_status', '!=', 'out_of_stock'))

                # Product labels
                if filters.get('labels'):
                    domain.append(('product_label', 'in', filters['labels']))

                # Search term
                if filters.get('search'):
                    search_term = filters['search']
                    domain.extend([
                        '|', '|',
                        ('name', 'ilike', search_term),
                        ('description_sale', 'ilike', search_term),
                        ('short_description', 'ilike', search_term)
                    ])

            # Get total count
            total_count = request.env['product.template'].sudo().search_count(domain)

            # Get products
            offset = (page - 1) * limit
            order = filters.get('order', 'website_sequence desc') if filters else 'website_sequence desc'
            products = request.env['product.template'].sudo().search(
                domain,
                limit=limit,
                offset=offset,
                order=order
            )

            # Prepare product data
            product_data = []
            for product in products:
                product_data.append({
                    'id': product.id,
                    'name': product.name,
                    'price': product.list_price,
                    'compare_price': product.compare_list_price,
                    'discount_percentage': product.discount_percentage,
                    'image_url': f'/web/image/product.template/{product.id}/image_1024',
                    'url': f'/shop/product/{product.id}',
                    'stock_status': product.stock_status,
                    'product_label': product.product_label,
                    'brand': product.brand_id.name if product.brand_id else '',
                    'short_description': product.short_description or '',
                })

            return {
                'success': True,
                'products': product_data,
                'total_count': total_count,
                'page': page,
                'total_pages': (total_count + limit - 1) // limit
            }

        except Exception as e:
            _logger.error(f"Product filter error: {str(e)}")
            return {'error': str(e)}