# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.http import request


class ProductComparison(models.Model):
    _name = 'product.comparison'
    _description = 'Product Comparison'
    _order = 'create_date desc'

    name = fields.Char(
        string='Comparison Name',
        required=True,
        default=lambda self: _('Product Comparison')
    )

    product_ids = fields.Many2many(
        'product.template',
        'product_comparison_rel',
        'comparison_id',
        'product_id',
        string='Products to Compare'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        default=lambda self: self.env.user.partner_id
    )

    session_id = fields.Char(
        string='Session ID',
        help='For anonymous users'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.model
    def get_comparison_for_user(self):
        """Get or create comparison for current user/session"""
        if self.env.user._is_public():
            session_id = request.session.sid if request else False
            if session_id:
                comparison = self.search([
                    ('session_id', '=', session_id),
                    ('active', '=', True)
                ], limit=1)
                if not comparison:
                    comparison = self.create({
                        'session_id': session_id,
                        'name': _('Product Comparison')
                    })
                return comparison
        else:
            comparison = self.search([
                ('partner_id', '=', self.env.user.partner_id.id),
                ('active', '=', True)
            ], limit=1)
            if not comparison:
                comparison = self.create({
                    'partner_id': self.env.user.partner_id.id,
                    'name': _('Product Comparison')
                })
            return comparison
        return self.env['product.comparison']

    def add_product(self, product_id):
        """Add product to comparison"""
        product = self.env['product.template'].browse(product_id)
        if product and product not in self.product_ids:
            self.product_ids = [(4, product_id)]
            return True
        return False

    def remove_product(self, product_id):
        """Remove product from comparison"""
        if product_id in self.product_ids.ids:
            self.product_ids = [(3, product_id)]
            return True
        return False

    def get_comparison_attributes(self):
        """Get all comparison attributes for products"""
        all_attributes = {}

        for product in self.product_ids:
            for attr in product.comparison_attributes:
                if attr.name not in all_attributes:
                    all_attributes[attr.name] = {
                        'name': attr.name,
                        'type': attr.attribute_type,
                        'values': {},
                        'highlighted': attr.is_highlighted
                    }
                all_attributes[attr.name]['values'][product.id] = attr.value

        return all_attributes


class ProductWishlist(models.Model):
    _name = 'product.wishlist'
    _description = 'Product Wishlist'
    _rec_name = 'product_id'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        ondelete='cascade'
    )

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product Template',
        related='product_id.product_tmpl_id',
        store=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        ondelete='cascade'
    )

    date_added = fields.Datetime(
        string='Date Added',
        default=fields.Datetime.now
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    _sql_constraints = [
        ('unique_user_product', 'unique(partner_id, product_id)',
         'Product already exists in wishlist!')
    ]

    @api.model
    def toggle_product(self, product_id, partner_id=None):
        """Toggle product in wishlist"""
        if not partner_id:
            partner_id = self.env.user.partner_id.id

        wishlist_item = self.search([
            ('partner_id', '=', partner_id),
            ('product_id', '=', product_id)
        ])

        if wishlist_item:
            wishlist_item.unlink()
            return False
        else:
            self.create({
                'partner_id': partner_id,
                'product_id': product_id
            })
            return True

    @api.model
    def is_in_wishlist(self, product_id, partner_id=None):
        """Check if product is in wishlist"""
        if not partner_id:
            if self.env.user._is_public():
                return False
            partner_id = self.env.user.partner_id.id

        return bool(self.search([
            ('partner_id', '=', partner_id),
            ('product_id', '=', product_id)
        ]))


class ProductRecentlyViewed(models.Model):
    _name = 'product.recently.viewed'
    _description = 'Recently Viewed Products'
    _order = 'date_viewed desc'

    product_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
        ondelete='cascade'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer'
    )

    session_id = fields.Char(
        string='Session ID',
        help='For anonymous users'
    )

    date_viewed = fields.Datetime(
        string='Date Viewed',
        default=fields.Datetime.now
    )

    view_count = fields.Integer(
        string='View Count',
        default=1
    )

    @api.model
    def add_product_view(self, product_id):
        """Add or update product view"""
        partner_id = None
        session_id = None

        if not self.env.user._is_public():
            partner_id = self.env.user.partner_id.id
        else:
            session_id = request.session.sid if request else False

        if partner_id or session_id:
            domain = [('product_id', '=', product_id)]
            if partner_id:
                domain.append(('partner_id', '=', partner_id))
            else:
                domain.append(('session_id', '=', session_id))

            existing = self.search(domain, limit=1)
            if existing:
                existing.write({
                    'date_viewed': fields.Datetime.now(),
                    'view_count': existing.view_count + 1
                })
            else:
                self.create({
                    'product_id': product_id,
                    'partner_id': partner_id,
                    'session_id': session_id,
                })

    @api.model
    def get_recent_products(self, limit=10):
        """Get recently viewed products"""
        domain = []
        if not self.env.user._is_public():
            domain = [('partner_id', '=', self.env.user.partner_id.id)]
        else:
            session_id = request.session.sid if request else False
            if session_id:
                domain = [('session_id', '=', session_id)]
            else:
                return self.env['product.template']

        recent_views = self.search(domain, limit=limit)
        return recent_views.mapped('product_id')