/* Shasha E-Commerce Main JavaScript */

(function($) {
    'use strict';

    // Global variables
    window.ShashaStore = {
        cart: {
            items: [],
            total: 0,
            count: 0
        },
        wishlist: [],
        comparison: [],
        settings: {
            currency: '$',
            animationDuration: 300,
            showNotifications: true,
            autoHideNotifications: 5000
        }
    };

    // Initialize on document ready
    $(document).ready(function() {
        initializeStore();
        bindEvents();
        loadCartData();
        initializeTooltips();
        initializeModals();
    });

    // Initialize store functionality
    function initializeStore() {
        console.log('Shasha Store initialized');
        updateCartUI();
        loadWishlistData();
        loadComparisonData();
        initializeProductHovers();
    }

    // Bind all event listeners
    function bindEvents() {
        // Cart events
        $(document).on('click', '.add-to-cart-btn', handleAddToCart);
        $(document).on('click', '.remove-from-cart-btn', handleRemoveFromCart);
        $(document).on('click', '.qty-btn', handleQuantityChange);

        // Wishlist events
        $(document).on('click', '.wishlist-btn', handleWishlistToggle);

        // Comparison events
        $(document).on('click', '.compare-btn', handleComparisonToggle);

        // Quick view events
        $(document).on('click', '.quick-view-btn', handleQuickView);

        // Layout toggle events
        $(document).on('click', '.layout-toggle', handleLayoutToggle);

        // Filter events
        $(document).on('change', '.filter-checkbox', handleFilterChange);
        $(document).on('submit', '.filter-form', handleFilterSubmit);
    }

    // Cart functionality
    function handleAddToCart(e) {
        e.preventDefault();
        const $btn = $(this);
        const productId = $btn.data('product-id');
        const quantity = $btn.data('quantity') || 1;

        if (!productId) {
            showNotification('Error: Product ID not found', 'error');
            return;
        }

        // Show loading state
        $btn.prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> Adding...');

        // Create a form and submit it (standard Odoo way)
        const form = $('<form>', {
            'method': 'POST',
            'action': '/shop/cart/update'
        });

        form.append($('<input>', {
            'type': 'hidden',
            'name': 'product_id',
            'value': productId
        }));

        form.append($('<input>', {
            'type': 'hidden',
            'name': 'add_qty',
            'value': quantity
        }));

        // Add CSRF token if available
        const csrfToken = $('meta[name="csrf-token"]').attr('content') ||
                         $('input[name="csrf_token"]').val();
        if (csrfToken) {
            form.append($('<input>', {
                'type': 'hidden',
                'name': 'csrf_token',
                'value': csrfToken
            }));
        }

        $('body').append(form);
        form.submit();

        // Note: Page will redirect/reload with the updated cart
    }

    function handleRemoveFromCart(e) {
        e.preventDefault();
        const $btn = $(this);
        const lineId = $btn.data('line-id');

        if (!lineId) return;

        $btn.prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i>');

        $.ajax({
            url: '/shop/cart/update_json',
            type: 'POST',
            dataType: 'json',
            data: {
                line_id: lineId,
                set_qty: 0
            },
            success: function(data) {
                updateCartData(data);
                $btn.closest('.cart-item').fadeOut(300, function() {
                    $(this).remove();
                });
                showNotification('Product removed from cart', 'info');
            },
            error: function() {
                showNotification('Error removing product', 'error');
                $btn.prop('disabled', false).html('<i class="fa fa-trash"></i>');
            }
        });
    }

    function handleQuantityChange(e) {
        e.preventDefault();
        const $btn = $(this);
        const change = parseInt($btn.data('change')) || 0;
        const $qtySpan = $btn.siblings('.cart-item-qty');
        const currentQty = parseInt($qtySpan.text()) || 1;
        const newQty = Math.max(1, currentQty + change);
        const lineId = $btn.closest('.cart-item').data('line-id');

        if (newQty === currentQty) return;

        $.ajax({
            url: '/shop/cart/update_json',
            type: 'POST',
            dataType: 'json',
            data: {
                line_id: lineId,
                set_qty: newQty
            },
            success: function(data) {
                updateCartData(data);
                $qtySpan.text(newQty);
                updateCartItemTotal($btn.closest('.cart-item'), data);
            },
            error: function() {
                showNotification('Error updating quantity', 'error');
            }
        });
    }

    // Wishlist functionality
    function handleWishlistToggle(e) {
        e.preventDefault();
        const $btn = $(this);
        const productId = $btn.data('product-id');

        if (!productId) return;

        $btn.prop('disabled', true);

        $.ajax({
            url: '/shop/wishlist/toggle',
            type: 'POST',
            dataType: 'json',
            data: {
                product_id: productId
            },
            success: function(data) {
                if (data.in_wishlist) {
                    $btn.addClass('active').html('<i class="fa fa-heart text-danger"></i>');
                    showNotification('Added to wishlist', 'success');
                } else {
                    $btn.removeClass('active').html('<i class="fa fa-heart-o"></i>');
                    showNotification('Removed from wishlist', 'info');
                }
            },
            error: function() {
                showNotification('Error updating wishlist', 'error');
            },
            complete: function() {
                $btn.prop('disabled', false);
            }
        });
    }

    // Comparison functionality
    function handleComparisonToggle(e) {
        e.preventDefault();
        const $btn = $(this);
        const productId = $btn.data('product-id');

        if (!productId) return;

        $.ajax({
            url: '/shop/compare/add/' + productId,
            type: 'POST',
            dataType: 'json',
            success: function(data) {
                if (data.success) {
                    $btn.addClass('active');
                    showNotification(data.message, 'success');
                    updateComparisonCount();
                } else {
                    showNotification(data.message, 'warning');
                }
            },
            error: function() {
                showNotification('Error updating comparison', 'error');
            }
        });
    }

    // Quick view functionality
    function handleQuickView(e) {
        e.preventDefault();
        const $btn = $(this);
        const productId = $btn.data('product-id');

        if (!productId) return;

        $btn.prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i>');

        $.ajax({
            url: '/shop/product/quick_view/' + productId,
            type: 'POST',
            dataType: 'json',
            success: function(data) {
                if (data.product) {
                    showQuickViewModal(data.product);
                } else {
                    showNotification('Product not found', 'error');
                }
            },
            error: function() {
                showNotification('Error loading product details', 'error');
            },
            complete: function() {
                $btn.prop('disabled', false).html('<i class="fa fa-eye"></i>');
            }
        });
    }

    // Layout toggle functionality
    function handleLayoutToggle(e) {
        e.preventDefault();
        const $btn = $(this);
        const layout = $btn.data('layout');

        $('.layout-toggle').removeClass('active');
        $btn.addClass('active');

        if (layout === 'grid') {
            $('#products-list').hide();
            $('#products-grid').show();
        } else {
            $('#products-grid').hide();
            $('#products-list').show();
        }

        // Save preference
        localStorage.setItem('preferred_layout', layout);
    }

    // Filter functionality
    function handleFilterChange(e) {
        const $checkbox = $(this);
        const $form = $checkbox.closest('form');

        // Auto-submit form when filter changes
        setTimeout(function() {
            $form.submit();
        }, 100);
    }

    function handleFilterSubmit(e) {
        e.preventDefault();
        const $form = $(this);
        const formData = $form.serialize();

        // Add loading state
        showLoadingOverlay();

        // Update URL and reload content
        window.location.href = '?' + formData;
    }

    // UI Update functions
    function updateCartData(data) {
        ShashaStore.cart.count = data.cart_quantity || 0;
        ShashaStore.cart.total = data.amount_total || 0;
        ShashaStore.cart.currency = data.currency_symbol || '$';

        updateCartUI();
    }

    function updateCartUI() {
        const count = ShashaStore.cart.count;
        const total = ShashaStore.cart.total;
        const currency = ShashaStore.cart.currency;

        // Update cart count badge
        const $countBadge = $('#cartCountBadge, .cart-count-badge, #floatingCartCount');
        if (count > 0) {
            $countBadge.text(count).show();
        } else {
            $countBadge.hide();
        }

        // Update cart total
        $('#cartTotal, #cartGrandTotal, .cart-total').text(currency + total.toFixed(2));

        // Update cart items count
        $('#cartItemCount').text(count + ' item' + (count !== 1 ? 's' : ''));

        // Show/hide empty cart message
        if (count === 0) {
            $('#emptyCartMessage').show();
            $('#cartFooter, #cartDivider').hide();
        } else {
            $('#emptyCartMessage').hide();
            $('#cartFooter, #cartDivider').show();
        }

        // Show/hide floating cart
        if (count > 0) {
            $('#floatingCart').fadeIn();
        } else {
            $('#floatingCart').fadeOut();
        }
    }

    function updateCartItemTotal($item, data) {
        // Update individual cart item total if needed
        const lineId = $item.data('line-id');
        if (data.order_lines) {
            const line = data.order_lines.find(l => l.id === lineId);
            if (line) {
                $item.find('.cart-item-price').text(ShashaStore.cart.currency + line.price_total.toFixed(2));
            }
        }
    }

    // Modal functions
    function showAddToCartModal(productId, quantity) {
        // Implementation would populate and show the add to cart success modal
        if (ShashaStore.settings.showNotifications) {
            $('#addToCartModal').modal('show');
        }
    }

    function showQuickViewModal(product) {
        const modalContent = `
            <div class="row">
                <div class="col-md-6">
                    <img src="data:image/jpeg;base64,${product.image_1920}" alt="${product.name}" class="img-fluid rounded">
                </div>
                <div class="col-md-6">
                    <h5>${product.name}</h5>
                    ${product.brand ? '<p class="text-muted">Brand: ' + product.brand + '</p>' : ''}
                    <div class="price mb-3">
                        <span class="h4 text-primary">${product.currency}${product.price}</span>
                        ${product.has_discounted_price ? '<span class="text-muted text-decoration-line-through ms-2">' + product.currency + product.list_price + '</span>' : ''}
                    </div>
                    ${product.description_sale ? '<p>' + product.description_sale + '</p>' : ''}
                    <div class="d-grid">
                        <button class="btn btn-primary add-to-cart-btn" data-product-id="${product.id}">
                            <i class="fa fa-shopping-cart me-1"></i> Add to Cart
                        </button>
                    </div>
                </div>
            </div>
        `;

        $('#quickViewContent').html(modalContent);
        $('#quickViewModal').modal('show');
    }

    // Notification system
    function showNotification(message, type = 'info') {
        if (!ShashaStore.settings.showNotifications) return;

        const alertClass = type === 'error' ? 'danger' : type;
        const icon = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle'
        }[type] || 'info-circle';

        const notification = $(`
            <div class="alert alert-${alertClass} alert-dismissible fade show shadow" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                <i class="fa fa-${icon} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);

        $('body').append(notification);

        if (ShashaStore.settings.autoHideNotifications > 0) {
            setTimeout(() => {
                notification.alert('close');
            }, ShashaStore.settings.autoHideNotifications);
        }
    }

    // Loading states
    function showLoadingOverlay() {
        if ($('#loadingOverlay').length === 0) {
            const overlay = $(`
                <div id="loadingOverlay" class="position-fixed w-100 h-100 d-flex align-items-center justify-content-center" style="top: 0; left: 0; background: rgba(255,255,255,0.8); z-index: 9998;">
                    <div class="text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <div class="mt-2">Loading...</div>
                    </div>
                </div>
            `);
            $('body').append(overlay);
        }
    }

    function hideLoadingOverlay() {
        $('#loadingOverlay').remove();
    }

    // Initialize tooltips and other Bootstrap components
    function initializeTooltips() {
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }

    function initializeModals() {
        // Initialize any custom modal functionality
    }

    // Product hover effects
    function initializeProductHovers() {
        $('.product-card').hover(
            function() {
                $(this).find('.product-actions-overlay, .quick-add-btn').stop(true, true).fadeIn(200);
            },
            function() {
                $(this).find('.product-actions-overlay, .quick-add-btn').stop(true, true).fadeOut(200);
            }
        );
    }

    // Load data functions
    function loadCartData() {
        // Use standard Odoo cart data from page context
        // The cart data will be available in the page template
        console.log('Cart data will be loaded from page context');
    }

    function loadWishlistData() {
        // Load wishlist data if user is logged in
    }

    function loadComparisonData() {
        // Load comparison data from session
    }

    function updateComparisonCount() {
        // Update comparison count in UI
    }

    // Utility functions
    function formatCurrency(amount) {
        return ShashaStore.settings.currency + amount.toFixed(2);
    }

    function debounce(func, delay) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }

    // Expose global functions
    window.addToCart = function(element) {
        $(element).trigger('click');
    };

    window.toggleWishlist = function(element) {
        $(element).trigger('click');
    };

    window.addToCompare = function(element) {
        $(element).trigger('click');
    };

    window.quickView = function(element) {
        $(element).trigger('click');
    };

    window.setLayoutMode = function(mode) {
        $(`.layout-toggle[data-layout="${mode}"]`).trigger('click');
    };

    window.sortProducts = function(order) {
        const url = new URL(window.location);
        url.searchParams.set('order', order);
        window.location.href = url.toString();
    };

    window.quickAddToCart = function(element) {
        $(element).addClass('add-to-cart-btn').trigger('click');
    };

    window.updateCartQuantity = function(element, change) {
        $(element).data('change', change).addClass('qty-btn').trigger('click');
    };

    window.removeFromCart = function(element) {
        $(element).addClass('remove-from-cart-btn').trigger('click');
    };

})(jQuery);