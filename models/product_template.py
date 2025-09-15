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
    ], string='Product Label', help='Label to display on product card')
    
    short_description = fields.Text(
        string='Short Description',
        help='Brief description for product cards'
    )
    
    technical_specs = fields.Html(
        string='Technical Specifications',
        help='Detailed technical specifications'
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
            brand.product_count = len(brand.product_ids)
    
    product_ids = fields.One2many(
        'product.template',
        'brand_id',
        string='Products'
    )