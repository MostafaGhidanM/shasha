{
    'name': 'TechDream Mobile Theme',
    'version': '1.0.0',
    'category': 'Theme/eCommerce',
    'summary': 'Complete e-commerce theme for TechDream Mobile',
    'description': """
        TechDream Mobile Theme
        ======================
        
        A complete e-commerce theme inspired by modern mobile phone retailers.
        
        Features:
        - Professional homepage with hero slider
        - Advanced product catalog with filters
        - Detailed product pages
        - Shopping cart and checkout process
        - Responsive design for all devices
        - Contact page with forms
        - SEO optimized structure
    """,
    'author': 'TechDream',
    'website': 'https://www.techdream.ae',
    'depends': [
        'base',
        'website',
        'website_sale',
        'sale',
        'stock',
        'product',
        'payment',
        'website_payment',
        'website_blog',
        'portal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/theme.xml',
        'views/shop_templates.xml',
        'views/product_templates.xml',
        'views/cart_checkout_templates.xml',
        'views/contact_templates.xml',
        'data/website_data.xml',
        'data/product_categories.xml',
        'data/sample_products.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'techdream_theme/static/src/css/techdream.css',
            'techdream_theme/static/src/js/techdream.js',
            'techdream_theme/static/src/js/cart.js',
            'techdream_theme/static/src/js/product.js',
        ],
    },
    'demo': [
        'demo/demo_products.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/theme_screenshot.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
    'price': 0,
    'currency': 'EUR',
    'live_test_url': 'https://www.techdream.ae',
}