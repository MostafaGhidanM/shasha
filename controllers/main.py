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
        
        return request.render('techdream_theme.techdream_homepage_enhanced', values)


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
        
        # Get brands for filter - check if brand model exists
        brands = []
        try:
            brands = request.env['product.brand'].sudo().search([]) if 'product.brand' in request.env else []
        except:
            brands = []
        
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
        
        return request.render('techdream_theme.shop_page_template', values)

    @http.route(['/shop/category/<model("product.public.category"):category>'], type='http', auth="public", website=True)
    def category(self, category, **post):
        """Category page"""
        return self.shop(category=category.id, **post)

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        """Enhanced product detail page"""
        
        # Get product variants
        variants = product.product_variant_ids.filtered(lambda v: v.active)
        
        # Get related products
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
        
        values = {
            'product': product,
            'variants': variants,
            'related_products': related_products,
            'reviews': reviews,
            'specifications': specifications,
            'category': category,
            'search': search,
        }
        
        return request.render('techdream_theme.product_detail_template', values)

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
        
        return request.render('techdream_theme.cart_page_template', values)

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        """Enhanced checkout page"""
        order = request.website.sale_get_order()
        
        if not order or not order.order_line:
            return request.redirect('/shop')
        
        # Get shipping methods - check if delivery.carrier has website_published
        try:
            shipping_methods = request.env['delivery.carrier'].sudo().search([
                ('website_published', '=', True)
            ])
        except:
            # Fallback if website_published doesn't exist
            shipping_methods = request.env['delivery.carrier'].sudo().search([
                ('active', '=', True)
            ])
        
        # Get payment methods - check if payment.provider has website_published
        try:
            payment_methods = request.env['payment.provider'].sudo().search([
                ('state', 'in', ['enabled', 'test']),
                ('website_published', '=', True)
            ])
        except:
            # Fallback if website_published doesn't exist
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
        
        return request.render('techdream_theme.checkout_page_template', values)


class TechDreamContact(http.Controller):
    """Contact page controller"""

    @http.route(['/contact'], type='http', auth="public", website=True)
    def contact(self, **kwargs):
        """Contact page"""
        values = {
            'success': kwargs.get('success', False),
            'error': kwargs.get('error', False),
        }
        return request.render('techdream_theme.contact_page_template', values)

    @http.route(['/contact/submit'], type='http', auth="public", website=True, csrf=False)
    def contact_submit(self, **post):
        """Handle contact form submission"""
        try:
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'subject', 'message']
            for field in required_fields:
                if not post.get(field):
                    return request.redirect('/contact?error=missing_fields')
            
            # Create lead or send email
            if 'crm.lead' in request.env:
                # Create CRM lead if CRM is installed
                request.env['crm.lead'].sudo().create({
                    'name': f"Contact Form: {post.get('subject')}",
                    'contact_name': f"{post.get('first_name')} {post.get('last_name')}",
                    'email_from': post.get('email'),
                    'phone': post.get('phone', ''),
                    'description': post.get('message'),
                    'source_id': request.env.ref('utm.utm_source_website').id,
                })
            else:
                # Send email if CRM is not available
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

    @http.route(['/api/wishlist/toggle'], type='json', auth="public", website=True)
    def wishlist_toggle(self, product_id):
        """Toggle product in wishlist"""
        if not request.env.user._is_public():
            try:
                product = request.env['product.template'].sudo().browse(product_id)
                if not product.exists():
                    return {'error': 'Product not found'}
                
                wishlist = request.env['product.wishlist'].sudo().search([
                    ('partner_id', '=', request.env.user.partner_id.id),
                    ('product_id', '=', product.product_variant_id.id)
                ])
                
                if wishlist:
                    wishlist.unlink()
                    in_wishlist = False
                else:
                    request.env['product.wishlist'].sudo().create({
                        'partner_id': request.env.user.partner_id.id,
                        'product_id': product.product_variant_id.id,
                    })
                    in_wishlist = True
                
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
        
        values.update({
            'partner': partner,
            'recent_orders': orders,
            'wishlist_items': wishlist_items,
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
        if 'blog.blog' in request.env:
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
                    "src": "/techdream_theme/static/src/img/icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/techdream_theme/static/src/img/icon-512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ]
        }
        
        return request.make_response(
            json.dumps(manifest),
            [('Content-Type', 'application/json')]
        )