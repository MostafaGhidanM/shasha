# -*- coding: utf-8 -*-

from odoo import http
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
            ('website_published', '=', True),
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
        return request.render('shasha.brand_products', {
            'brand': brand,
            'products': products,
        })


class ShashaWebsiteSale(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True, brand=None, **kwargs):
        """Override to add brand filtering"""
        domain = super()._get_search_domain(search, category, attrib_values, search_in_description, **kwargs)

        if brand:
            domain += [('brand_id', '=', int(brand))]

        return domain

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
        '/shop/brand/<int:brand>',
        '/shop/brand/<int:brand>/page/<int:page>',
    ], type='http', auth='public', website=True, sitemap=True)
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        """Enhanced shop with brand filtering"""
        add_qty = int(post.get('add_qty', 1))
        try:
            min_price = float(min_price)
        except ValueError:
            min_price = 0
        try:
            max_price = float(max_price)
        except ValueError:
            max_price = 0

        category_id = None
        if category:
            category_id = category.id

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split('-')] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        keep = QueryURL('/shop',
                       category=category_id,
                       search=search,
                       attrib=attrib_list,
                       min_price=min_price,
                       max_price=max_price,
                       order=post.get('order'))

        now = fields.Datetime.now()
        pricelist = request.env['website'].get_current_website().pricelist_id

        domain = self._get_search_domain(
            search, category, attrib_values,
            brand=post.get('brand'),
            **post
        )

        if min_price or max_price:
            price_domain = self._get_search_price_domain(min_price, max_price)
            domain += price_domain

        website = request.env['website'].get_current_website()
        products = request.env['product.template'].search(domain)

        search_count = len(products)

        # Pagination
        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = website.shop_ppg or 20

        pager = request.website.pager(
            url=request.httprequest.path.partition('?')[0],
            url_args=post,
            total=search_count,
            page=page,
            step=ppg,
            scope=7,
            url_anchor='products_grid',
        )

        offset = pager['offset']
        products = products[offset:offset + ppg]

        # Get available brands
        available_brands = request.env['product.brand'].search([
            ('website_published', '=', True),
            ('active', '=', True),
        ])

        # Get product attributes for filtering
        ProductAttribute = request.env['product.attribute']
        attributes = ProductAttribute.search([('attribute_line_ids.product_tmpl_id', 'in', products.ids)])

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': search_count,
            'bins': TableCompute().process(products, ppg),
            'ppg': ppg,
            'ppr': website.shop_ppr or 4,
            'categories': request.env['product.public.category'].search([('parent_id', '=', False)]),
            'brands': available_brands,
            'selected_brand': int(post.get('brand', 0)),
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': category.search([]).ids,
            'layout_mode': request.session.get('website_sale_shop_layout_mode', 'grid'),
        }

        return request.render('shasha.shop_page', values)


from odoo.addons.website.models.website import QueryURL
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo import fields