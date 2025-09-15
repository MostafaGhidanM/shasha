// ====================
// File: techdream.js - Main JavaScript functionality
// ====================

(function() {
    'use strict';

    // DOM Ready
    document.addEventListener('DOMContentLoaded', function() {
        initTechDream();
    });

    function initTechDream() {
        // Initialize all components
        initSearchAutocomplete();
        initMobileMenu();
        initProductCarousel();
        initScrollToTop();
        initLazyLoading();
        initTooltips();
        updateCartCounter();
        initProductComparison();
        initWishlist();
        initInventoryCheck();
        initQuickView();
    }

    // Search Autocomplete
    function initSearchAutocomplete() {
        const searchInput = document.querySelector('.search-input');
        if (!searchInput) return;

        let searchTimeout;
        let resultsContainer;

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();

            if (query.length < 2) {
                hideSearchResults();
                return;
            }

            searchTimeout = setTimeout(() => {
                searchProducts(query);
            }, 300);
        });

        searchInput.addEventListener('blur', function() {
            setTimeout(hideSearchResults, 200);
        });

        function searchProducts(query) {
            fetch('/api/products/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    params: { query: query, limit: 8 }
                })
            })
            .then(response => response.json())
            .then(data => {
                showSearchResults(data.result.products);
            })
            .catch(error => {
                console.error('Search error:', error);
            });
        }

        function showSearchResults(products) {
            if (!resultsContainer) {
                resultsContainer = document.createElement('div');
                resultsContainer.className = 'search-results';
                resultsContainer.style.cssText = `
                    position: absolute;
                    top: 100%;
                    left: 0;
                    right: 0;
                    background: white;
                    border: 1px solid #ddd;
                    border-top: none;
                    border-radius: 0 0 8px 8px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    z-index: 1000;
                    max-height: 400px;
                    overflow-y: auto;
                `;
                searchInput.parentNode.appendChild(resultsContainer);
                searchInput.parentNode.style.position = 'relative';
            }

            resultsContainer.innerHTML = '';

            if (products.length === 0) {
                resultsContainer.innerHTML = '<div class="p-3 text-muted">No products found</div>';
                return;
            }

            products.forEach(product => {
                const item = document.createElement('div');
                item.className = 'search-result-item';
                item.style.cssText = `
                    display: flex;
                    align-items: center;
                    padding: 12px;
                    border-bottom: 1px solid #f0f0f0;
                    cursor: pointer;
                    transition: background 0.2s;
                `;
                
                item.innerHTML = `
                    <img src="${product.image_url}" alt="${product.name}" 
                         style="width: 40px; height: 40px; object-fit: contain; margin-right: 12px; border-radius: 4px;">
                    <div style="flex: 1;">
                        <div style="font-weight: 500; color: #2c3e50;">${product.name}</div>
                        <div style="color: #e74c3c; font-weight: 600;">${product.currency} ${product.price}</div>
                    </div>
                `;

                item.addEventListener('mouseenter', function() {
                    this.style.background = '#f8f9fa';
                });

                item.addEventListener('mouseleave', function() {
                    this.style.background = 'white';
                });

                item.addEventListener('click', function() {
                    window.location.href = product.url;
                });

                resultsContainer.appendChild(item);
            });
        }

        function hideSearchResults() {
            if (resultsContainer) {
                resultsContainer.style.display = 'none';
            }
        }
    }

    // Mobile Menu
    function initMobileMenu() {
        const menuToggle = document.createElement('button');
        menuToggle.className = 'mobile-menu-toggle d-md-none';
        menuToggle.innerHTML = '<i class="fas fa-bars"></i>';
        menuToggle.style.cssText = `
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            padding: 10px;
            cursor: pointer;
        `;

        const mainNav = document.querySelector('.main-nav');
        if (mainNav) {
            mainNav.appendChild(menuToggle);

            menuToggle.addEventListener('click', function() {
                const navMenu = document.querySelector('.nav-menu');
                if (navMenu.style.display === 'block') {
                    navMenu.style.display = 'none';
                    this.innerHTML = '<i class="fas fa-bars"></i>';
                } else {
                    navMenu.style.display = 'block';
                    this.innerHTML = '<i class="fas fa-times"></i>';
                }
            });
        }
    }

    // Product Carousel for homepage
    function initProductCarousel() {
        const carousels = document.querySelectorAll('.products-grid');
        carousels.forEach(carousel => {
            if (carousel.children.length > 4) {
                // Add navigation arrows if more than 4 products
                addCarouselNavigation(carousel);
            }
        });
    }

    function addCarouselNavigation(carousel) {
        const wrapper = document.createElement('div');
        wrapper.className = 'carousel-wrapper';
        wrapper.style.position = 'relative';
        
        carousel.parentNode.insertBefore(wrapper, carousel);
        wrapper.appendChild(carousel);

        const prevBtn = document.createElement('button');
        prevBtn.className = 'carousel-nav carousel-prev';
        prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
        prevBtn.style.cssText = `
            position: absolute;
            left: -20px;
            top: 50%;
            transform: translateY(-50%);
            background: #3498db;
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            cursor: pointer;
            z-index: 10;
            transition: background 0.3s;
        `;

        const nextBtn = document.createElement('button');
        nextBtn.className = 'carousel-nav carousel-next';
        nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
        nextBtn.style.cssText = prevBtn.style.cssText.replace('left: -20px', 'right: -20px');

        wrapper.appendChild(prevBtn);
        wrapper.appendChild(nextBtn);

        let currentIndex = 0;
        const itemsToShow = 4;
        const totalItems = carousel.children.length;

        function updateCarousel() {
            const translateX = -(currentIndex * (100 / itemsToShow));
            carousel.style.transform = `translateX(${translateX}%)`;
        }

        prevBtn.addEventListener('click', function() {
            currentIndex = Math.max(0, currentIndex - 1);
            updateCarousel();
        });

        nextBtn.addEventListener('click', function() {
            currentIndex = Math.min(totalItems - itemsToShow, currentIndex + 1);
            updateCarousel();
        });
    }

    // Scroll to Top
    function initScrollToTop() {
        const scrollBtn = document.createElement('button');
        scrollBtn.className = 'scroll-to-top';
        scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        scrollBtn.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            cursor: pointer;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s;
            box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
        `;

        document.body.appendChild(scrollBtn);

        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollBtn.style.opacity = '1';
                scrollBtn.style.visibility = 'visible';
            } else {
                scrollBtn.style.opacity = '0';
                scrollBtn.style.visibility = 'hidden';
            }
        });

        scrollBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Lazy Loading for Images
    function initLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }

    // Tooltips
    function initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', showTooltip);
            element.addEventListener('mouseleave', hideTooltip);
        });

        function showTooltip(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = e.target.dataset.tooltip;
            tooltip.style.cssText = `
                position: absolute;
                background: #333;
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 10000;
                pointer-events: none;
                white-space: nowrap;
            `;

            document.body.appendChild(tooltip);

            const rect = e.target.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';

            e.target._tooltip = tooltip;
        }

        function hideTooltip(e) {
            if (e.target._tooltip) {
                e.target._tooltip.remove();
                delete e.target._tooltip;
            }
        }
    }

    // Update Cart Counter
    function updateCartCounter() {
        fetch('/shop/cart/quantity')
            .then(response => response.json())
            .then(data => {
                const cartCount = document.querySelector('.cart-count');
                if (cartCount && data.cart_quantity !== undefined) {
                    cartCount.textContent = data.cart_quantity;
                    cartCount.style.display = data.cart_quantity > 0 ? 'block' : 'none';
                }
            })
            .catch(error => {
                console.error('Cart counter update error:', error);
            });
    }

    // Notification System
    window.showNotification = function(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#27ae60' : '#e74c3c'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            z-index: 10000;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        `;

        notification.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span>${message}</span>
                <button onclick="this.parentNode.parentNode.remove()" 
                        style="background: none; border: none; color: white; margin-left: 10px; cursor: pointer;">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);

        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    };

    // Product Comparison Functions
    function initProductComparison() {
        updateComparisonCounter();
    }

    window.addToComparison = function(button) {
        const productId = parseInt(button.dataset.productId);

        fetch('/api/compare/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                params: { product_id: productId }
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.result.success) {
                showNotification(data.result.message);
                updateComparisonCounter();
                button.classList.add('btn-primary');
                button.classList.remove('btn-outline-secondary');
                button.innerHTML = '<i class="fa fa-check"></i> Added';
            } else {
                showNotification(data.result.error || 'Error adding to comparison', 'error');
            }
        })
        .catch(error => {
            console.error('Comparison error:', error);
            showNotification('Error adding to comparison', 'error');
        });
    };

    window.removeFromComparison = function(button) {
        const productId = parseInt(button.dataset.productId);

        fetch('/api/compare/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                params: { product_id: productId }
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.result.success) {
                showNotification(data.result.message);
                updateComparisonCounter();
                // Remove the product card or reload page
                window.location.reload();
            }
        })
        .catch(error => {
            console.error('Comparison remove error:', error);
        });
    };

    window.clearComparison = function() {
        if (confirm('Are you sure you want to clear all products from comparison?')) {
            fetch('/api/compare/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ params: {} })
            })
            .then(response => response.json())
            .then(data => {
                if (data.result.success) {
                    showNotification(data.result.message);
                    window.location.reload();
                }
            });
        }
    };

    function updateComparisonCounter() {
        const comparisonCount = document.querySelector('.comparison-count');
        if (comparisonCount) {
            // Update comparison counter logic
            fetch('/api/compare/count')
                .then(response => response.json())
                .then(data => {
                    comparisonCount.textContent = data.count || 0;
                    comparisonCount.style.display = data.count > 0 ? 'block' : 'none';
                })
                .catch(error => console.error('Comparison counter error:', error));
        }
    }

    // Wishlist Functions
    function initWishlist() {
        updateWishlistCounter();
    }

    window.toggleWishlist = function(button) {
        const productId = parseInt(button.dataset.productId);

        fetch('/api/wishlist/toggle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                params: { product_id: productId }
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.result.success) {
                const icon = button.querySelector('i');
                if (data.result.in_wishlist) {
                    icon.className = 'fa fa-heart';
                    button.classList.add('active');
                    showNotification('Added to wishlist');
                } else {
                    icon.className = 'fa fa-heart-o';
                    button.classList.remove('active');
                    showNotification('Removed from wishlist');
                }
                updateWishlistCounter();
            } else {
                showNotification(data.result.error || 'Please login to use wishlist', 'error');
            }
        })
        .catch(error => {
            console.error('Wishlist error:', error);
            showNotification('Error updating wishlist', 'error');
        });
    };

    window.moveToCart = function(button) {
        const productId = parseInt(button.dataset.productId);

        fetch('/api/wishlist/move_to_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                params: { product_id: productId, quantity: 1 }
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.result.success) {
                showNotification(data.result.message);
                updateCartCounter();
                updateWishlistCounter();
                // Remove the item from wishlist page
                const productCard = button.closest('.wishlist-item');
                if (productCard) {
                    productCard.remove();
                }
            } else {
                showNotification(data.result.error || 'Error moving to cart', 'error');
            }
        })
        .catch(error => {
            console.error('Move to cart error:', error);
        });
    };

    function updateWishlistCounter() {
        const wishlistCount = document.querySelector('.wishlist-count');
        if (wishlistCount) {
            // This would require an API endpoint to get wishlist count
            fetch('/api/wishlist/count')
                .then(response => response.json())
                .then(data => {
                    wishlistCount.textContent = data.count || 0;
                    wishlistCount.style.display = data.count > 0 ? 'block' : 'none';
                })
                .catch(error => console.error('Wishlist counter error:', error));
        }
    }

    // Inventory Check Functions
    function initInventoryCheck() {
        // Auto-check inventory for products on page
        const productCards = document.querySelectorAll('[data-product-id]');
        productCards.forEach(card => {
            const productId = card.dataset.productId;
            if (productId) {
                checkInventory(productId, card);
            }
        });
    }

    window.checkInventory = function(productId, element) {
        fetch('/api/inventory/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                params: { product_id: parseInt(productId), quantity: 1 }
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.result) {
                updateInventoryDisplay(element, data.result);
            }
        })
        .catch(error => {
            console.error('Inventory check error:', error);
        });
    };

    function updateInventoryDisplay(element, inventoryData) {
        const stockBadge = element.querySelector('.stock-badge');
        const addToCartBtn = element.querySelector('.add-to-cart-btn');

        if (stockBadge) {
            stockBadge.className = 'badge stock-badge';

            switch (inventoryData.stock_status) {
                case 'out_of_stock':
                    stockBadge.classList.add('bg-danger');
                    stockBadge.textContent = 'Out of Stock';
                    break;
                case 'low_stock':
                    stockBadge.classList.add('bg-warning');
                    stockBadge.textContent = 'Low Stock';
                    break;
                default:
                    stockBadge.classList.add('bg-success');
                    stockBadge.textContent = 'In Stock';
            }
        }

        if (addToCartBtn && inventoryData.stock_status === 'out_of_stock') {
            addToCartBtn.disabled = true;
            addToCartBtn.innerHTML = '<i class="fa fa-ban"></i> Out of Stock';
        }
    }

    // Quick View Functions
    function initQuickView() {
        // Initialize quick view modals
        const quickViewBtns = document.querySelectorAll('.quick-view-btn');
        quickViewBtns.forEach(btn => {
            btn.addEventListener('click', handleQuickView);
        });
    }

    function handleQuickView(event) {
        const button = event.target.closest('.quick-view-btn');
        const productId = button.dataset.productId;

        // Create and show modal with product details
        createQuickViewModal(productId);
    }

    function createQuickViewModal(productId) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Quick View</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="text-center">
                            <div class="spinner-border" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Load product details
        fetch(`/shop/product/${productId}?quick_view=1`)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const productContent = doc.querySelector('.product-details');

                if (productContent) {
                    modal.querySelector('.modal-body').innerHTML = productContent.outerHTML;
                }
            })
            .catch(error => {
                console.error('Quick view error:', error);
                modal.querySelector('.modal-body').innerHTML = '<p>Error loading product details</p>';
            });

        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Clean up when modal is hidden
        modal.addEventListener('hidden.bs.modal', function() {
            modal.remove();
        });
    }

    // Enhanced Cart Functions
    window.addToCart = function(button, productId, quantity = 1) {
        button.disabled = true;
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Adding...';

        fetch('/api/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                params: {
                    product_id: parseInt(productId),
                    quantity: quantity
                }
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.result.success) {
                showNotification('Product added to cart!');
                updateCartCounter();
                button.innerHTML = '<i class="fa fa-check"></i> Added!';
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.disabled = false;
                }, 2000);
            } else {
                showNotification(data.result.error || 'Error adding to cart', 'error');
                button.innerHTML = originalText;
                button.disabled = false;
            }
        })
        .catch(error => {
            console.error('Add to cart error:', error);
            showNotification('Error adding to cart', 'error');
            button.innerHTML = originalText;
            button.disabled = false;
        });
    };

    // Product Filtering
    window.filterProducts = function(filters) {
        const loader = document.querySelector('.products-loader');
        const productsContainer = document.querySelector('.products-container');

        if (loader) loader.style.display = 'block';

        fetch('/api/products/filter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                params: { filters: filters }
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.result.success && productsContainer) {
                updateProductsDisplay(data.result.products, productsContainer);
            }
        })
        .catch(error => {
            console.error('Filter error:', error);
        })
        .finally(() => {
            if (loader) loader.style.display = 'none';
        });
    };

    function updateProductsDisplay(products, container) {
        // Update products display with filtered results
        let html = '';
        products.forEach(product => {
            html += generateProductCard(product);
        });
        container.innerHTML = html;

        // Re-initialize functionality for new elements
        initInventoryCheck();
    }

    function generateProductCard(product) {
        return `
            <div class="col-md-4 col-lg-3 mb-4">
                <div class="card product-card h-100" data-product-id="${product.id}">
                    <div class="position-relative">
                        <img src="${product.image_url}" class="card-img-top" alt="${product.name}" style="height: 200px; object-fit: cover;">
                        <span class="badge stock-badge position-absolute" style="top: 10px; left: 10px;"></span>
                        ${product.discount_percentage > 0 ? `<span class="badge bg-danger position-absolute" style="top: 10px; right: 10px;">${product.discount_percentage}% OFF</span>` : ''}
                    </div>
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">${product.name}</h5>
                        <p class="card-text flex-grow-1">${product.short_description}</p>
                        <div class="price-section mb-3">
                            <span class="h5 text-primary">$${product.price}</span>
                            ${product.compare_price > 0 ? `<del class="text-muted ms-2">$${product.compare_price}</del>` : ''}
                        </div>
                        <div class="btn-group w-100">
                            <button class="btn btn-primary add-to-cart-btn" onclick="addToCart(this, ${product.id})">Add to Cart</button>
                            <button class="btn btn-outline-secondary compare-btn" onclick="addToComparison(this)" data-product-id="${product.id}"><i class="fa fa-balance-scale"></i></button>
                            <button class="btn btn-outline-danger wishlist-btn" onclick="toggleWishlist(this)" data-product-id="${product.id}"><i class="fa fa-heart-o"></i></button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Global utility functions
    window.TechDream = {
        updateCartCounter: updateCartCounter,
        showNotification: window.showNotification,
        addToCart: window.addToCart,
        toggleWishlist: window.toggleWishlist,
        addToComparison: window.addToComparison,
        filterProducts: window.filterProducts,
        checkInventory: window.checkInventory,
    };

})();