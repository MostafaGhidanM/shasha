// ====================
// File: cart.js - Cart functionality
// ====================

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        initCartFunctionality();
    });

    function initCartFunctionality() {
        initAddToCartButtons();
        initCartQuantityControls();
        initRemoveFromCart();
        initCartTotalsUpdate();
    }

    // Add to Cart Buttons
    function initAddToCartButtons() {
        const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
        
        addToCartButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const productId = this.dataset.productId || 
                    this.closest('[data-product-id]')?.dataset.productId;
                
                if (!productId) {
                    console.error('Product ID not found');
                    return;
                }

                const quantity = parseInt(document.querySelector('#quantity')?.value) || 1;
                
                // Show loading state
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
                this.disabled = true;

                addToCart(productId, quantity)
                    .then(result => {
                        if (result.success) {
                            TechDream.showNotification('Product added to cart!');
                            TechDream.updateCartCounter();
                            
                            // Optional: Add cart animation
                            animateCartIcon();
                        } else {
                            TechDream.showNotification(result.error || 'Failed to add to cart', 'error');
                        }
                    })
                    .finally(() => {
                        this.innerHTML = originalText;
                        this.disabled = false;
                    });
            });
        });
    }

    // Cart Quantity Controls
    function initCartQuantityControls() {
        const qtyControls = document.querySelectorAll('.quantity-controls');
        
        qtyControls.forEach(control => {
            const minusBtn = control.querySelector('.qty-btn[onclick*="decrease"], .qty-btn:first-child');
            const plusBtn = control.querySelector('.qty-btn[onclick*="increase"], .qty-btn:last-child');
            const input = control.querySelector('.qty-input');
            
            if (minusBtn) {
                minusBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    updateQuantity(input, -1);
                });
            }
            
            if (plusBtn) {
                plusBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    updateQuantity(input, 1);
                });
            }
            
            if (input) {
                input.addEventListener('change', function() {
                    const lineId = this.closest('tr')?.dataset.lineId;
                    if (lineId) {
                        updateCartQuantity(lineId, parseInt(this.value));
                    }
                });
            }
        });
    }

    function updateQuantity(input, change) {
        const currentValue = parseInt(input.value) || 1;
        const newValue = Math.max(1, currentValue + change);
        input.value = newValue;
        
        // Trigger change event for cart updates
        input.dispatchEvent(new Event('change'));
    }

    // Remove from Cart
    function initRemoveFromCart() {
        const removeButtons = document.querySelectorAll('.remove-item');
        
        removeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const lineId = this.closest('tr')?.dataset.lineId;
                if (lineId) {
                    if (confirm('Remove this item from cart?')) {
                        removeCartLine(lineId);
                    }
                }
            });
        });
    }

    // Cart API Functions
    function addToCart(productId, quantity = 1, options = {}) {
        return fetch('/api/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                params: {
                    product_id: parseInt(productId),
                    quantity: quantity,
                    ...options
                }
            })
        })
        .then(response => response.json())
        .then(data => data.result);
    }

    function updateCartQuantity(lineId, quantity) {
        return fetch('/api/cart/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                params: {
                    line_id: parseInt(lineId),
                    quantity: quantity
                }
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.result.success) {
                updateCartTotals(data.result);
                TechDream.updateCartCounter();
            }
            return data.result;
        });
    }

    function removeCartLine(lineId) {
        return fetch('/api/cart/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                params: {
                    line_id: parseInt(lineId)
                }
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.result.success) {
                // Remove the row from table
                const row = document.querySelector(`tr[data-line-id="${lineId}"]`);
                if (row) {
                    row.remove();
                }
                updateCartTotals(data.result);
                TechDream.updateCartCounter();
                TechDream.showNotification('Item removed from cart');
            }
            return data.result;
        });
    }

    // Update Cart Totals
    function initCartTotalsUpdate() {
        // This will be called after cart operations
    }

    function updateCartTotals(cartData) {
        // Update subtotal
        const subtotalElement = document.querySelector('.cart-subtotal');
        if (subtotalElement && cartData.cart_total !== undefined) {
            subtotalElement.textContent = `${cartData.currency} ${cartData.cart_total.toFixed(2)}`;
        }
        
        // Update total
        const totalElement = document.querySelector('.cart-total');
        if (totalElement && cartData.cart_total !== undefined) {
            // Add tax and shipping if needed
            const tax = cartData.cart_total * 0.05; // 5% tax
            const total = cartData.cart_total + tax;
            totalElement.textContent = `${cartData.currency} ${total.toFixed(2)}`;
        }
    }

    // Cart Animation
    function animateCartIcon() {
        const cartIcon = document.querySelector('.cart-icon');
        if (cartIcon) {
            cartIcon.style.transform = 'scale(1.2)';
            cartIcon.style.transition = 'transform 0.2s';
            
            setTimeout(() => {
                cartIcon.style.transform = 'scale(1)';
            }, 200);
        }
    }

    // Expose cart functions globally
    window.CartManager = {
        addToCart: addToCart,
        updateQuantity: updateCartQuantity,
        removeItem: removeCartLine,
    };

})();
