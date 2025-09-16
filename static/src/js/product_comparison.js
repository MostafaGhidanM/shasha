/* Product Comparison JavaScript */

(function($) {
    'use strict';

    // Comparison functionality
    const ProductComparison = {
        maxProducts: 4,
        storageKey: 'shasha_comparison_list',

        init: function() {
            this.bindEvents();
            this.loadFromStorage();
            this.updateUI();
        },

        bindEvents: function() {
            $(document).on('click', '.add-to-compare', this.addProduct.bind(this));
            $(document).on('click', '.remove-from-compare', this.removeProduct.bind(this));
            $(document).on('click', '.clear-comparison', this.clearAll.bind(this));
            $(document).on('click', '.compare-products-btn', this.viewComparison.bind(this));
        },

        getComparisonList: function() {
            return JSON.parse(localStorage.getItem(this.storageKey) || '[]');
        },

        saveToStorage: function(list) {
            localStorage.setItem(this.storageKey, JSON.stringify(list));
        },

        loadFromStorage: function() {
            const saved = this.getComparisonList();
            this.updateProductButtons(saved);
        },

        addProduct: function(e) {
            e.preventDefault();
            const $btn = $(e.target);
            const productId = parseInt($btn.data('product-id'));

            if (!productId) {
                this.showMessage('Product ID not found', 'error');
                return;
            }

            let comparisonList = this.getComparisonList();

            // Check if product already in comparison
            if (comparisonList.includes(productId)) {
                this.showMessage('Product already in comparison', 'warning');
                return;
            }

            // Check maximum limit
            if (comparisonList.length >= this.maxProducts) {
                this.showMessage(`Maximum ${this.maxProducts} products can be compared`, 'warning');
                return;
            }

            // Add product to comparison
            comparisonList.push(productId);
            this.saveToStorage(comparisonList);

            // Update UI
            $btn.addClass('active btn-warning')
                .removeClass('btn-outline-secondary')
                .attr('title', 'Remove from comparison')
                .find('i').removeClass('fa-balance-scale').addClass('fa-check');

            this.updateComparisonCount();
            this.showMessage('Product added to comparison', 'success');
            this.showComparisonBar();
        },

        removeProduct: function(e) {
            e.preventDefault();
            const $btn = $(e.target);
            const productId = parseInt($btn.data('product-id'));

            if (!productId) return;

            let comparisonList = this.getComparisonList();
            comparisonList = comparisonList.filter(id => id !== productId);
            this.saveToStorage(comparisonList);

            // Update UI
            $btn.removeClass('active btn-warning')
                .addClass('btn-outline-secondary')
                .attr('title', 'Add to comparison')
                .find('i').removeClass('fa-check').addClass('fa-balance-scale');

            this.updateComparisonCount();
            this.showMessage('Product removed from comparison', 'info');

            // Hide comparison bar if empty
            if (comparisonList.length === 0) {
                this.hideComparisonBar();
            }

            // If on comparison page, remove the column
            if (window.location.pathname === '/shop/compare') {
                this.removeProductColumn(productId);
            }
        },

        clearAll: function(e) {
            if (e) e.preventDefault();

            if (confirm('Are you sure you want to clear all products from comparison?')) {
                localStorage.removeItem(this.storageKey);

                // Reset all buttons
                $('.add-to-compare').removeClass('active btn-warning')
                    .addClass('btn-outline-secondary')
                    .attr('title', 'Add to comparison')
                    .find('i').removeClass('fa-check').addClass('fa-balance-scale');

                this.updateComparisonCount();
                this.hideComparisonBar();
                this.showMessage('Comparison cleared', 'info');

                // If on comparison page, redirect to shop
                if (window.location.pathname === '/shop/compare') {
                    window.location.href = '/shop';
                }
            }
        },

        viewComparison: function(e) {
            e.preventDefault();
            const comparisonList = this.getComparisonList();

            if (comparisonList.length < 2) {
                this.showMessage('Add at least 2 products to compare', 'warning');
                return;
            }

            window.location.href = '/shop/compare';
        },

        updateComparisonCount: function() {
            const count = this.getComparisonList().length;

            // Update comparison count in UI
            $('.comparison-count').text(count);

            // Show/hide comparison button
            if (count > 1) {
                $('.comparison-actions').show();
            } else {
                $('.comparison-actions').hide();
            }
        },

        updateProductButtons: function(comparisonList) {
            comparisonList.forEach(productId => {
                $(`.add-to-compare[data-product-id="${productId}"]`)
                    .addClass('active btn-warning')
                    .removeClass('btn-outline-secondary')
                    .attr('title', 'Remove from comparison')
                    .find('i').removeClass('fa-balance-scale').addClass('fa-check');
            });
        },

        showComparisonBar: function() {
            if ($('#comparisonBar').length === 0) {
                const comparisonBar = $(`
                    <div id="comparisonBar" class="comparison-bar position-fixed bottom-0 start-0 end-0 bg-primary text-white p-3 shadow" style="z-index: 1050;">
                        <div class="container">
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <div class="d-flex align-items-center">
                                        <i class="fa fa-balance-scale fa-lg me-2"></i>
                                        <span class="me-3">
                                            <span class="comparison-count">0</span> product(s) in comparison
                                        </span>
                                        <div class="comparison-actions" style="display: none;">
                                            <button class="btn btn-light btn-sm me-2 compare-products-btn">
                                                <i class="fa fa-eye me-1"></i> Compare Now
                                            </button>
                                            <button class="btn btn-outline-light btn-sm clear-comparison">
                                                <i class="fa fa-trash me-1"></i> Clear All
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="comparison-products d-flex justify-content-end" id="comparisonThumbnails">
                                        <!-- Product thumbnails will be added here -->
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `);
                $('body').append(comparisonBar);

                // Add margin to body to prevent content overlap
                $('body').css('margin-bottom', '100px');
            }

            $('#comparisonBar').slideDown();
            this.updateComparisonCount();
        },

        hideComparisonBar: function() {
            $('#comparisonBar').slideUp(function() {
                $(this).remove();
                $('body').css('margin-bottom', '0');
            });
        },

        removeProductColumn: function(productId) {
            // Remove product column from comparison table
            const columnIndex = $(`.comparison-table th[data-product-id="${productId}"]`).index();
            if (columnIndex > 0) {
                $(`.comparison-table tr`).each(function() {
                    $(this).find('th, td').eq(columnIndex).fadeOut(300, function() {
                        $(this).remove();
                    });
                });
            }

            // If no products left, show empty state
            setTimeout(() => {
                if ($('.comparison-table th[data-product-id]').length === 0) {
                    $('.comparison-table-wrapper').fadeOut(300);
                    $('.empty-comparison').fadeIn(300);
                }
            }, 300);
        },

        updateUI: function() {
            const comparisonList = this.getComparisonList();

            if (comparisonList.length > 0) {
                this.showComparisonBar();
                this.updateProductButtons(comparisonList);
            }
        },

        showMessage: function(message, type = 'info') {
            // Use the global notification system
            if (typeof showNotification === 'function') {
                showNotification(message, type);
            } else {
                // Fallback alert
                alert(message);
            }
        },

        // API methods for external use
        getCount: function() {
            return this.getComparisonList().length;
        },

        isInComparison: function(productId) {
            return this.getComparisonList().includes(parseInt(productId));
        },

        getProducts: function() {
            return this.getComparisonList();
        }
    };

    // Comparison table functionality for comparison page
    const ComparisonTable = {
        init: function() {
            if ($('.comparison-table').length > 0) {
                this.bindEvents();
                this.makeResponsive();
            }
        },

        bindEvents: function() {
            $(document).on('click', '.remove-from-comparison', ProductComparison.removeProduct.bind(ProductComparison));
            $(document).on('click', '.add-to-cart-from-compare', this.addToCartFromCompare.bind(this));
        },

        makeResponsive: function() {
            const $table = $('.comparison-table');
            const $wrapper = $table.closest('.table-responsive');

            if ($(window).width() < 768) {
                $wrapper.addClass('comparison-mobile');
            }

            // Handle horizontal scrolling
            let isScrolling = false;
            $wrapper.on('scroll', function() {
                if (!isScrolling) {
                    $wrapper.addClass('scrolling');
                    isScrolling = true;

                    setTimeout(() => {
                        $wrapper.removeClass('scrolling');
                        isScrolling = false;
                    }, 150);
                }
            });
        },

        addToCartFromCompare: function(e) {
            e.preventDefault();
            const $btn = $(e.target);
            const productId = $btn.data('product-id');

            // Trigger the global add to cart functionality
            if (typeof addToCart === 'function') {
                addToCart($btn[0]);
            } else {
                // Fallback AJAX call
                $.ajax({
                    url: '/shop/cart/update_json',
                    type: 'POST',
                    data: {
                        product_id: productId,
                        add_qty: 1
                    },
                    success: function(data) {
                        ProductComparison.showMessage('Product added to cart!', 'success');
                    },
                    error: function() {
                        ProductComparison.showMessage('Error adding product to cart', 'error');
                    }
                });
            }
        },

        highlightDifferences: function() {
            // Highlight differences in attribute values
            $('.comparison-table tbody tr').each(function() {
                const $row = $(this);
                const $cells = $row.find('td:not(:first-child)');
                const values = [];

                $cells.each(function() {
                    values.push($(this).text().trim());
                });

                // Check if all values are different
                const uniqueValues = [...new Set(values)];
                if (uniqueValues.length > 1) {
                    $row.addClass('has-differences');
                }
            });
        }
    };

    // Initialize when document is ready
    $(document).ready(function() {
        ProductComparison.init();
        ComparisonTable.init();
    });

    // Expose to global scope
    window.ProductComparison = ProductComparison;
    window.ComparisonTable = ComparisonTable;

    // Global helper functions
    window.addToCompare = function(element) {
        $(element).trigger('click');
    };

    window.removeFromCompare = function(element) {
        $(element).trigger('click');
    };

    window.clearComparison = function() {
        ProductComparison.clearAll();
    };

    window.viewComparison = function() {
        ProductComparison.viewComparison({ preventDefault: function() {} });
    };

})(jQuery);