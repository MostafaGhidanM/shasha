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

    // Global utility functions
    window.TechDream = {
        updateCartCounter: updateCartCounter,
        showNotification: window.showNotification,
    };

})();