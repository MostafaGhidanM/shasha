# Shasha E-Commerce Module for Odoo

A comprehensive e-commerce solution that integrates seamlessly with Odoo's built-in modules to provide a modern, feature-rich online store experience.

## Features

### 🎨 **Modern UI/UX Design**
- Responsive design that works on all devices
- Clean, professional interface with Bootstrap 5
- Smooth animations and hover effects
- Mobile-optimized shopping experience

### 🏠 **Enhanced Homepage**
- Hero slider with call-to-action buttons
- Featured products showcase
- Product categories display
- Brand showcase section
- Best sellers and latest products sections

### 🛒 **Advanced Shop Features**
- Product cards with quick actions
- Advanced filtering system (by category, brand, price, attributes)
- Grid and list view options
- Product comparison functionality
- Wishlist management
- Product search with filters
- Sorting options (price, name, date, popularity)

### 🛍️ **Shopping Cart**
- AJAX-powered cart updates
- Cart dropdown widget
- Floating cart button
- Mini cart notifications
- Quick add to cart functionality

### 📱 **Product Features**
- Product brands management
- Featured products marking
- Product badges and labels
- Product image sliders
- Quick view modals
- Product comparison (up to 4 products)

### 🔧 **Integration with Odoo**
- Seamlessly integrates with Odoo's built-in modules:
  - `product` - Product management
  - `sale` - Sales orders
  - `stock` - Inventory management
  - `website_sale` - E-commerce functionality
  - `portal` - Customer portal

## Installation

### Prerequisites
- Odoo 17.0 or later
- Required Odoo modules:
  - `website`
  - `website_sale`
  - `product`
  - `sale`
  - `stock`
  - `portal`
  - `website_sale_comparison`

### Installation Steps

1. **Copy the module to your Odoo addons directory:**
   ```bash
   cp -r shasha /path/to/your/odoo/addons/
   ```

2. **Update the addons list:**
   - Go to Apps menu in Odoo
   - Click "Update Apps List"
   - Search for "Shasha E-Commerce"

3. **Install the module:**
   - Click "Install" on the Shasha E-Commerce module
   - The module will automatically install its dependencies

4. **Configure your website:**
   - Go to Website → Configuration → Settings
   - Enable the necessary e-commerce features
   - Configure your payment methods and shipping options

## Configuration

### 1. **Product Setup**
```python
# Create product brands
brand = env['product.brand'].create({
    'name': 'Your Brand Name',
    'description': 'Brand description',
    'website_published': True,
})

# Mark products as featured
product = env['product.template'].browse(product_id)
product.write({
    'is_featured': True,
    'brand_id': brand.id,
    'badge_text': 'New',
    'badge_color': 'primary',
})
```

### 2. **Website Menu Configuration**
The module automatically creates main navigation menus:
- Home (/)
- Shop (/shop)
- Categories (/shop)
- Brands (/brands)
- About (/about)
- Contact (/contact)

### 3. **Customization Options**
You can customize the module by:
- Modifying CSS variables in `/static/src/css/main.css`
- Adjusting JavaScript settings in `/static/src/js/main.js`
- Customizing templates in `/views/` directory

## Module Structure

```
shasha/
├── __init__.py
├── __manifest__.py
├── README.md
├── controllers/
│   ├── __init__.py
│   ├── main.py          # Main website routes
│   ├── shop.py          # Shop functionality
│   └── api.py           # API endpoints
├── models/
│   ├── __init__.py
│   ├── product_brand.py # Brand management
│   ├── product_wishlist.py # Wishlist functionality
│   ├── sale_order.py    # Enhanced sale orders
│   └── website.py       # Website extensions
├── views/
│   ├── homepage_templates.xml    # Homepage templates
│   ├── shop_templates.xml       # Shop page templates
│   ├── product_templates.xml    # Product display templates
│   ├── cart_templates.xml       # Cart functionality templates
│   └── website_templates.xml    # Additional page templates
├── data/
│   ├── website_menu_data.xml    # Navigation menu data
│   └── website_page_data.xml    # Static pages data
├── security/
│   └── ir.model.access.csv      # Access rights
└── static/
    └── src/
        ├── css/
        │   ├── main.css         # Main styles
        │   ├── homepage.css     # Homepage styles
        │   ├── shop.css         # Shop page styles
        │   ├── product.css      # Product page styles
        │   └── cart.css         # Cart styles
        ├── js/
        │   ├── main.js          # Main JavaScript
        │   ├── homepage.js      # Homepage functionality
        │   └── product_comparison.js # Comparison feature
        └── images/
            └── (image assets)
```

## API Endpoints

The module provides several AJAX endpoints for dynamic functionality:

### Product APIs
- `POST /api/products/featured` - Get featured products
- `POST /api/products/latest` - Get latest products
- `POST /api/products/bestsellers` - Get best selling products

### Cart APIs
- `POST /shop/cart/update_json` - Update cart items
- `POST /api/cart/summary` - Get cart summary

### Wishlist APIs
- `POST /shop/wishlist/toggle` - Toggle wishlist items

### Comparison APIs
- `POST /shop/compare/add/<int:product_id>` - Add to comparison
- `POST /shop/compare/remove/<int:product_id>` - Remove from comparison
- `POST /shop/compare/clear` - Clear comparison

## Customization

### CSS Customization
Modify the CSS variables in `main.css`:
```css
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    /* ... more variables */
}
```

### JavaScript Configuration
Adjust settings in `main.js`:
```javascript
window.ShashaStore = {
    settings: {
        currency: '$',
        animationDuration: 300,
        showNotifications: true,
        autoHideNotifications: 5000
    }
};
```

### Template Customization
Override templates by inheriting from them:
```xml
<template id="custom_homepage" inherit_id="shasha.homepage">
    <!-- Your customizations -->
</template>
```

## Troubleshooting

### Common Issues

1. **Module not appearing in Apps list:**
   - Ensure the module is in the correct addons directory
   - Update the apps list from Apps menu

2. **Templates not loading:**
   - Check if all dependencies are installed
   - Restart the Odoo server
   - Update the module

3. **JavaScript not working:**
   - Check browser console for errors
   - Ensure jQuery is loaded
   - Verify asset paths in manifest

4. **Styles not applying:**
   - Clear browser cache
   - Check if CSS files are being served correctly
   - Verify asset bundle configuration

### Debug Mode
Enable debug mode to troubleshoot issues:
```bash
# Add to Odoo configuration
debug_mode = True
```

## Support

For support and questions:
- Check the Odoo documentation
- Review the module's code comments
- Test in a development environment first

## Contributing

To contribute to this module:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This module is licensed under LGPL-3. See the license file for details.

## Changelog

### Version 17.0.1.0.0
- Initial release
- Complete e-commerce functionality
- Modern responsive design
- Integration with Odoo built-in modules
- Product comparison feature
- Advanced cart functionality
- Wishlist management
- Brand management
- API endpoints for AJAX functionality

---

**Built with ❤️ for the Odoo Community**