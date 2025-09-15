# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_featured = fields.Boolean(
        string='Featured Product',
        default=False,
        help='Mark this product as featured to display on homepage'
    )

    brand_id = fields.Many2one(
        'product.brand',
        string='Brand',
        help='Product brand'
    )

    compare_list_price = fields.Float(
        string='Compare at Price',
        help='Price to compare against (usually the original price)',
        default=0.0
    )

    product_label = fields.Selection([
        ('new', 'New'),
        ('sale', 'Sale'),
        ('hot', 'Hot'),
        ('featured', 'Featured'),
        ('out_of_stock', 'Out of Stock'),
    ], string='Product Label', help='Label to display on product card')

    short_description = fields.Text(
        string='Short Description',
        help='Brief description for product cards'
    )

    technical_specs = fields.Html(
        string='Technical Specifications',
        help='Detailed technical specifications'
    )

    # Enhanced inventory integration
    stock_status = fields.Selection([
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    ], string='Stock Status', compute='_compute_stock_status', store=True)

    available_qty = fields.Float(
        string='Available Quantity',
        compute='_compute_available_qty',
        help='Total available quantity across all locations'
    )

    low_stock_threshold = fields.Float(
        string='Low Stock Threshold',
        default=10.0,
        help='Quantity below which product is considered low stock'
    )

    # Product comparison fields
    comparison_attributes = fields.One2many(
        'product.comparison.attribute',
        'product_id',
        string='Comparison Attributes'
    )

    # SEO fields
    meta_title = fields.Char(
        string='Meta Title',
        help='SEO meta title'
    )

    meta_description = fields.Text(
        string='Meta Description',
        help='SEO meta description'
    )

    meta_keywords = fields.Char(
        string='Meta Keywords',
        help='SEO meta keywords'
    )

    # Product gallery
    product_image_ids = fields.One2many(
        'product.image',
        'product_tmpl_id',
        string='Extra Product Images'
    )

    # Product videos
    video_url = fields.Char(
        string='Product Video URL',
        help='YouTube or Vimeo video URL'
    )

    # Product reviews
    review_count = fields.Integer(
        string='Review Count',
        compute='_compute_review_stats'
    )

    average_rating = fields.Float(
        string='Average Rating',
        compute='_compute_review_stats'
    )

    # Related products
    related_product_ids = fields.Many2many(
        'product.template',
        'product_related_rel',
        'product_id',
        'related_id',
        string='Related Products'
    )

    # Cross-sell products
    cross_sell_product_ids = fields.Many2many(
        'product.template',
        'product_cross_sell_rel',
        'product_id',
        'cross_sell_id',
        string='Cross-sell Products'
    )

    # Up-sell products
    up_sell_product_ids = fields.Many2many(
        'product.template',
        'product_up_sell_rel',
        'product_id',
        'up_sell_id',
        string='Up-sell Products'
    )
    
    @api.depends('list_price', 'compare_list_price')
    def _compute_discount_percentage(self):
        for product in self:
            if product.compare_list_price > 0 and product.list_price > 0:
                discount = ((product.compare_list_price - product.list_price) / product.compare_list_price) * 100
                product.discount_percentage = round(discount, 0)
            else:
                product.discount_percentage = 0

    discount_percentage = fields.Float(
        string='Discount %',
        compute='_compute_discount_percentage',
        store=True
    )

    @api.depends('product_variant_ids.qty_available')
    def _compute_available_qty(self):
        for product in self:
            product.available_qty = sum(product.product_variant_ids.mapped('qty_available'))

    @api.depends('available_qty', 'low_stock_threshold')
    def _compute_stock_status(self):
        for product in self:
            if product.available_qty <= 0:
                product.stock_status = 'out_of_stock'
            elif product.available_qty <= product.low_stock_threshold:
                product.stock_status = 'low_stock'
            else:
                product.stock_status = 'in_stock'

    @api.depends('message_ids')
    def _compute_review_stats(self):
        for product in self:
            reviews = product.message_ids.filtered(
                lambda m: m.message_type == 'comment' and
                         hasattr(m, 'rating_value') and
                         m.rating_value > 0
            )
            product.review_count = len(reviews)
            if reviews:
                product.average_rating = sum(reviews.mapped('rating_value')) / len(reviews)
            else:
                product.average_rating = 0.0

    def get_similar_products(self, limit=4):
        """Get similar products based on categories and attributes"""
        domain = [
            ('website_published', '=', True),
            ('id', '!=', self.id),
            ('public_categ_ids', 'in', self.public_categ_ids.ids)
        ]
        return self.env['product.template'].search(domain, limit=limit)

    def get_inventory_status(self):
        """Get detailed inventory status"""
        return {
            'qty_available': self.available_qty,
            'virtual_available': sum(self.product_variant_ids.mapped('virtual_available')),
            'incoming_qty': sum(self.product_variant_ids.mapped('incoming_qty')),
            'outgoing_qty': sum(self.product_variant_ids.mapped('outgoing_qty')),
            'stock_status': self.stock_status,
        }


class ProductComparisonAttribute(models.Model):
    _name = 'product.comparison.attribute'
    _description = 'Product Comparison Attribute'
    _order = 'sequence, name'

    name = fields.Char(
        string='Attribute Name',
        required=True
    )

    value = fields.Char(
        string='Attribute Value',
        required=True
    )

    product_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )

    attribute_type = fields.Selection([
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Yes/No'),
        ('selection', 'Selection'),
    ], string='Type', default='text')

    is_highlighted = fields.Boolean(
        string='Highlight in Comparison',
        default=False
    )


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'
    _order = 'name'

    name = fields.Char(
        string='Brand Name',
        required=True,
        translate=True
    )
    
    description = fields.Text(
        string='Description',
        translate=True
    )
    
    logo = fields.Binary(
        string='Logo',
        help='Brand logo image'
    )
    
    website_url = fields.Char(
        string='Website URL',
        help='Brand official website'
    )
    
    product_count = fields.Integer(
        string='Number of Products',
        compute='_compute_product_count'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    @api.depends('product_ids')
    def _compute_product_count(self):
        for brand in self:
            brand.product_count = len(brand.product_ids.filtered('website_published'))
    
    product_ids = fields.One2many(
        'product.template',
        'brand_id',
        string='Products'
    )

    website_published = fields.Boolean(
        string='Published on Website',
        default=True
    )

    meta_title = fields.Char(
        string='Meta Title',
        help='SEO meta title for brand page'
    )

    meta_description = fields.Text(
        string='Meta Description',
        help='SEO meta description for brand page'
    )

    def get_brand_products(self, limit=None):
        """Get published products for this brand"""
        domain = [
            ('brand_id', '=', self.id),
            ('website_published', '=', True)
        ]
        return self.env['product.template'].search(domain, limit=limit)