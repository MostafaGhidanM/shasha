{
    'name': 'TechDream Mobile Theme',
    'version': '17.0.1.0.0',
    'category': 'Website/Theme',
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
        'sale_management',
        'product',
        'stock',
        'delivery',
        'payment',
        'portal',
        'mail',
        'rating',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Data files
        'data/product_categories.xml',
        'data/sample_products.xml',
        'data/website_data.xml',
        'data/email_templates.xml',

        # Template files
        'views/theme.xml',
        'views/shop_templates.xml',
        'views/product_templates.xml',
        'views/cart_checkout_templates.xml',
        'views/contact_templates.xml',
        'views/comparison_templates.xml',
        'views/wishlist_templates.xml',
        'views/backend_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # Only include CSS/JS files if they actually exist
            'techdream_theme/static/src/css/techdream.css',
            'techdream_theme/static/src/js/techdream.js',
        ],
    },
    'images': [
        # Only include images if they exist
        # 'static/description/banner.png',
        # 'static/description/theme_screenshot.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}