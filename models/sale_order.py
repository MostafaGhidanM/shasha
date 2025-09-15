# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Enhanced ecommerce fields
    website_order_reference = fields.Char(
        string='Website Order Reference',
        help='Customer reference from website'
    )

    special_instructions = fields.Text(
        string='Special Instructions',
        help='Special delivery or handling instructions'
    )

    gift_message = fields.Text(
        string='Gift Message',
        help='Gift message for the order'
    )

    is_gift = fields.Boolean(
        string='Is Gift Order',
        default=False
    )

    coupon_code = fields.Char(
        string='Coupon Code',
        help='Applied coupon code'
    )

    # Delivery preferences
    preferred_delivery_date = fields.Date(
        string='Preferred Delivery Date'
    )

    delivery_time_slot = fields.Selection([
        ('morning', '9:00 AM - 12:00 PM'),
        ('afternoon', '12:00 PM - 6:00 PM'),
        ('evening', '6:00 PM - 9:00 PM'),
    ], string='Delivery Time Slot')

    # Order status for website
    website_order_status = fields.Selection([
        ('pending', 'Pending Payment'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ], string='Website Order Status', compute='_compute_website_order_status', store=True)

    # Tracking information
    tracking_number = fields.Char(
        string='Tracking Number',
        help='Shipment tracking number'
    )

    carrier_name = fields.Char(
        string='Carrier Name',
        help='Shipping carrier name'
    )

    estimated_delivery_date = fields.Date(
        string='Estimated Delivery Date'
    )

    @api.depends('state', 'invoice_status', 'picking_ids.state')
    def _compute_website_order_status(self):
        for order in self:
            if order.state == 'cancel':
                order.website_order_status = 'cancelled'
            elif order.state == 'draft':
                order.website_order_status = 'pending'
            elif order.state == 'sent':
                order.website_order_status = 'pending'
            elif order.state == 'sale':
                # Check delivery status
                pickings = order.picking_ids.filtered(lambda p: p.state != 'cancel')
                if all(p.state == 'done' for p in pickings) and pickings:
                    order.website_order_status = 'delivered'
                elif any(p.state in ['assigned', 'partially_available', 'confirmed'] for p in pickings):
                    order.website_order_status = 'shipped'
                else:
                    order.website_order_status = 'processing'
            else:
                order.website_order_status = 'processing'

    def send_order_confirmation_email(self):
        """Send order confirmation email"""
        template = self.env.ref('techdream_theme.email_template_order_confirmation', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

    def send_shipping_notification_email(self):
        """Send shipping notification email"""
        template = self.env.ref('techdream_theme.email_template_shipping_notification', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

    def get_order_progress_percentage(self):
        """Get order progress percentage for display"""
        status_progress = {
            'pending': 20,
            'processing': 40,
            'shipped': 70,
            'delivered': 100,
            'cancelled': 0,
            'refunded': 0,
        }
        return status_progress.get(self.website_order_status, 0)

    @api.model
    def get_customer_orders(self, partner_id, limit=None):
        """Get customer orders for portal"""
        domain = [
            ('partner_id', '=', partner_id),
            ('state', 'in', ['sale', 'done'])
        ]
        return self.search(domain, limit=limit, order='date_order desc')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Product customization
    product_customization = fields.Text(
        string='Product Customization',
        help='Customer product customization details'
    )

    # Gift wrapping
    gift_wrap = fields.Boolean(
        string='Gift Wrap',
        default=False
    )

    gift_wrap_fee = fields.Float(
        string='Gift Wrap Fee',
        default=0.0
    )

    # Line notes
    line_notes = fields.Text(
        string='Line Notes',
        help='Special notes for this order line'
    )

    @api.onchange('gift_wrap')
    def _onchange_gift_wrap(self):
        """Add gift wrap fee when gift wrap is selected"""
        if self.gift_wrap:
            # Get gift wrap fee from configuration
            gift_wrap_fee = self.env['ir.config_parameter'].sudo().get_param(
                'techdream_theme.gift_wrap_fee', 0.0)
            self.gift_wrap_fee = float(gift_wrap_fee)
        else:
            self.gift_wrap_fee = 0.0

    @api.depends('price_unit', 'discount', 'product_uom_qty', 'product_id', 'gift_wrap_fee')
    def _compute_amount(self):
        """Override to include gift wrap fee"""
        super()._compute_amount()
        for line in self:
            line.price_subtotal += line.gift_wrap_fee
            line.price_total += line.gift_wrap_fee


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Website integration
    website_tracking_url = fields.Char(
        string='Website Tracking URL',
        help='Tracking URL for customers'
    )

    def action_done(self):
        """Override to send shipping notification"""
        result = super().action_done()

        # Send shipping notification for website orders
        for picking in self:
            if picking.sale_id and picking.sale_id.website_id:
                picking.sale_id.send_shipping_notification_email()

                # Update tracking information
                if picking.carrier_tracking_ref:
                    picking.sale_id.tracking_number = picking.carrier_tracking_ref

        return result


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Customer preferences
    newsletter_subscription = fields.Boolean(
        string='Newsletter Subscription',
        default=False
    )

    preferred_language = fields.Selection(
        related='lang',
        string='Preferred Language'
    )

    birth_date = fields.Date(
        string='Birth Date'
    )

    # Customer statistics
    total_orders = fields.Integer(
        string='Total Orders',
        compute='_compute_customer_stats'
    )

    total_spent = fields.Float(
        string='Total Spent',
        compute='_compute_customer_stats'
    )

    last_order_date = fields.Date(
        string='Last Order Date',
        compute='_compute_customer_stats'
    )

    @api.depends('sale_order_ids')
    def _compute_customer_stats(self):
        for partner in self:
            orders = partner.sale_order_ids.filtered(lambda o: o.state in ['sale', 'done'])
            partner.total_orders = len(orders)
            partner.total_spent = sum(orders.mapped('amount_total'))
            partner.last_order_date = max(orders.mapped('date_order'), default=False)

    def get_customer_wishlist(self):
        """Get customer wishlist items"""
        return self.env['product.wishlist'].search([
            ('partner_id', '=', self.id)
        ])

    def get_recently_viewed_products(self, limit=10):
        """Get recently viewed products"""
        return self.env['product.recently.viewed'].search([
            ('partner_id', '=', self.id)
        ], limit=limit).mapped('product_id')