// ====================
// File: product.js - Product page functionality
// ====================

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        initProductPage();
    });

    function initProductPage() {
        initImageGallery();
        initProductOptions();
        initQuantityControls();
        initProductTabs();
        initWishlistToggle();
        initProductReviews();
    }

    // Image Gallery
    function initImageGallery() {
        const thumbnails = document.querySelectorAll('.thumbnail');
        const mainImage = document.getElementById('mainImage');
        
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                if (mainImage) {
                    mainImage.src = this.src;
                    
                    // Update active thumbnail
                    thumbnails.forEach(t => t.classList.remove('active'));
                    this.classList.add('active');
                }
            });
        });

        // Image zoom on hover
        if (mainImage) {
            mainImage.addEventListener('mousemove', function(e) {
                const rect = this.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const xPercent = (x / rect.width) * 100;
                const yPercent = (y / rect.height) * 100;
                
                this.style.transformOrigin = `${xPercent}% ${yPercent}%`;
                this.style.transform = 'scale(2)';
            });
            
            mainImage.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
            });
        }
    }

    // Product Options (Color, Size, etc.)
    function initProductOptions() {
        const optionButtons = document.querySelectorAll('.option-btn');
        
        optionButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from siblings
                const siblings = this.parentNode.querySelectorAll('.option-btn');
                siblings.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Update price if needed
                updateProductPrice();
            });
        });
    }

    function updateProductPrice() {
        // This would integrate with Odoo's variant pricing
        const activeOptions = document.querySelectorAll('.option-btn.active');
        const basePrice = parseFloat(document.querySelector('.price')?.dataset.basePrice || 0);
        
        // Calculate price based on selected options
        let finalPrice = basePrice;
        activeOptions.forEach(option => {
            const priceModifier = parseFloat(option.dataset.priceModifier || 0);
            finalPrice += priceModifier;
        });
        
        // Update displayed price
        const priceElement = document.querySelector('.price');
        if (priceElement) {
            const currency = priceElement.dataset.currency || 'AED';
            priceElement.textContent = `${currency} ${finalPrice.toFixed(0)}`;
        }
    }

    // Quantity Controls
    function initQuantityControls() {
        const qtyInput = document.getElementById('quantity');
        const minusBtn = document.querySelector('.qty-btn[onclick*="decrease"]');
        const plusBtn = document.querySelector('.qty-btn[onclick*="increase"]');
        
        if (minusBtn) {
            minusBtn.addEventListener('click', function(e) {
                e.preventDefault();
                if (qtyInput) {
                    const currentValue = parseInt(qtyInput.value) || 1;
                    qtyInput.value = Math.max(1, currentValue - 1);
                }
            });
        }
        
        if (plusBtn) {
            plusBtn.addEventListener('click', function(e) {
                e.preventDefault();
                if (qtyInput) {
                    const currentValue = parseInt(qtyInput.value) || 1;
                    const maxQty = parseInt(qtyInput.dataset.maxQty) || 999;
                    qtyInput.value = Math.min(maxQty, currentValue + 1);
                }
            });
        }
    }

    // Product Tabs
    function initProductTabs() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetTab = this.textContent.toLowerCase().replace(/\s+/g, '').replace(/[()]/g, '').split('(')[0];
                
                // Remove active class from all buttons and contents
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.style.display = 'none');
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Show corresponding content
                const targetContent = document.getElementById(targetTab);
                if (targetContent) {
                    targetContent.style.display = 'block';
                }
            });
        });
    }

    // Wishlist Toggle
    function initWishlistToggle() {
        const wishlistBtn = document.querySelector('.btn-wishlist');
        
        if (wishlistBtn) {
            wishlistBtn.addEventListener('click', function() {
                const productId = this.dataset.productId || 
                    document.querySelector('[data-product-id]')?.dataset.productId;
                
                if (!productId) return;
                
                const icon = this.querySelector('i');
                const originalClass = icon.className;
                
                // Show loading
                icon.className = 'fas fa-spinner fa-spin';
                
                toggleWishlist(productId)
                    .then(result => {
                        if (result.success) {
                            if (result.in_wishlist) {
                                icon.className = 'fas fa-heart';
                                this.style.background = '#e74c3c';
                                this.style.color = 'white';
                                TechDream.showNotification('Added to wishlist!');
                            } else {
                                icon.className = 'far fa-heart';
                                this.style.background = 'white';
                                this.style.color = '#e74c3c';
                                TechDream.showNotification('Removed from wishlist');
                            }
                        } else {
                            TechDream.showNotification(result.error || 'Please login to use wishlist', 'error');
                        }
                    })
                    .finally(() => {
                        if (icon.className.includes('spinner')) {
                            icon.className = originalClass;
                        }
                    });
            });
        }
    }

    function toggleWishlist(productId) {
        return fetch('/api/wishlist/toggle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                params: {
                    product_id: parseInt(productId)
                }
            })
        })
        .then(response => response.json())
        .then(data => data.result);
    }

    // Product Reviews
    function initProductReviews() {
        const reviewForm = document.querySelector('.review-form');
        
        if (reviewForm) {
            reviewForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const reviewData = {
                    rating: formData.get('rating'),
                    title: formData.get('title'),
                    comment: formData.get('comment'),
                };
                
                submitReview(reviewData);
            });
        }
        
        // Star rating interaction
        const starRatings = document.querySelectorAll('.star-rating');
        starRatings.forEach(rating => {
            const stars = rating.querySelectorAll('.star');
            stars.forEach((star, index) => {
                star.addEventListener('click', function() {
                    const value = index + 1;
                    
                    // Update visual state
                    stars.forEach((s, i) => {
                        if (i < value) {
                            s.classList.add('active');
                        } else {
                            s.classList.remove('active');
                        }
                    });
                    
                    // Update hidden input
                    const hiddenInput = rating.querySelector('input[name="rating"]');
                    if (hiddenInput) {
                        hiddenInput.value = value;
                    }
                });
            });
        });
    }

    function submitReview(reviewData) {
        // This would integrate with Odoo's review system
        console.log('Submitting review:', reviewData);
        TechDream.showNotification('Review submitted successfully!');
    }

    // Expose product functions globally
    window.ProductManager = {
        updatePrice: updateProductPrice,
        toggleWishlist: toggleWishlist,
    };

})();