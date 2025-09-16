# -*- coding: utf-8 -*-
{
    'name': 'Shasha E-Commerce',
    'version': '17.0.1.0.0',
    'category': 'Website/E-Commerce',
    'summary': 'Complete E-Commerce Solution with Modern UI',
    'description': """
        Shasha E-Commerce Module
        ========================

        A complete e-commerce solution that integrates with Odoo's built-in modules:

        Features:
        - Modern homepage with product slider
        - Complete shop with product cards and filters
        - Product comparison functionality
        - Advanced shopping cart
        - Integration with Odoo inventory, stock, and sales
        - Responsive design
        - SEO optimized
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'website',
        'website_sale',
        'product',
        'sale',
        'stock',
        'portal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/website_templates.xml',
        'views/homepage_templates.xml',
        'views/shop_templates.xml',
        'views/product_templates.xml',
        'views/cart_templates.xml',
        'data/website_page_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'shasha/static/src/css/main.css',
            'shasha/static/src/css/homepage.css',
            'shasha/static/src/css/shop.css',
            'shasha/static/src/css/product.css',
            'shasha/static/src/css/cart.css',
            'shasha/static/src/js/main.js',
            'shasha/static/src/js/homepage.js',
            'shasha/static/src/js/shop.js',
            'shasha/static/src/js/product_comparison.js',
            'shasha/static/src/js/cart.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}