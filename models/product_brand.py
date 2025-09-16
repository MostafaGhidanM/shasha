# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'
    _order = 'name'

    name = fields.Char('Brand Name', required=True)
    description = fields.Text('Description')
    image = fields.Image('Brand Logo', max_width=300, max_height=300)
    website_published = fields.Boolean('Published on Website', default=True)
    product_count = fields.Integer('Number of Products', compute='_compute_product_count')
    website_url = fields.Char('Website URL')
    active = fields.Boolean('Active', default=True)

    @api.depends('product_ids')
    def _compute_product_count(self):
        for brand in self:
            brand.product_count = len(brand.product_ids)

    product_ids = fields.One2many('product.template', 'brand_id', string='Products')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('product.brand', string='Brand')
    is_featured = fields.Boolean('Featured Product', default=False)
    badge_text = fields.Char('Product Badge')
    badge_color = fields.Selection([
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('success', 'Success'),
        ('danger', 'Danger'),
        ('warning', 'Warning'),
        ('info', 'Info'),
        ('light', 'Light'),
        ('dark', 'Dark'),
    ], string='Badge Color', default='primary')
    slider_image_ids = fields.One2many('product.slider.image', 'product_id', string='Slider Images')

    def _get_combination_info_variant(self, **kwargs):
        combination_info = super()._get_combination_info_variant(**kwargs)
        combination_info['brand_name'] = self.brand_id.name if self.brand_id else ''
        return combination_info


class ProductSliderImage(models.Model):
    _name = 'product.slider.image'
    _description = 'Product Slider Images'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True)
    image = fields.Image('Image', required=True, max_width=1920, max_height=1080)
    sequence = fields.Integer('Sequence', default=1)
    product_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade')
    active = fields.Boolean('Active', default=True)