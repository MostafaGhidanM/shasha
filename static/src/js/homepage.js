/* Homepage JavaScript */

(function($) {
    'use strict';

    const HomePage = {
        init: function() {
            this.initHeroSlider();
            this.initProductSliders();
            this.initCounters();
            this.initScrollAnimations();
            this.bindEvents();
        },

        initHeroSlider: function() {
            // Initialize hero section animations
            this.animateHeroElements();
        },

        initProductSliders: function() {
            // Initialize product carousel sliders if using any carousel library
            if (typeof Swiper !== 'undefined') {
                this.initSwiperSliders();
            } else {
                this.initBasicSliders();
            }
        },

        initSwiperSliders: function() {
            // Featured products slider
            new Swiper('.featured-products-slider', {
                slidesPerView: 1,
                spaceBetween: 20,
                navigation: {
                    nextEl: '.featured-next',
                    prevEl: '.featured-prev',
                },
                pagination: {
                    el: '.featured-pagination',
                    clickable: true,
                },
                breakpoints: {
                    576: {
                        slidesPerView: 2,
                    },
                    768: {
                        slidesPerView: 3,
                    },
                    1024: {
                        slidesPerView: 4,
                    },
                }
            });

            // Best sellers slider
            new Swiper('.bestsellers-slider', {
                slidesPerView: 1,
                spaceBetween: 20,
                autoplay: {
                    delay: 4000,
                    disableOnInteraction: false,
                },
                navigation: {
                    nextEl: '.bestsellers-next',
                    prevEl: '.bestsellers-prev',
                },
                breakpoints: {
                    576: {
                        slidesPerView: 2,
                    },
                    768: {
                        slidesPerView: 3,
                    },
                    1024: {
                        slidesPerView: 4,
                    },
                }
            });

            // Brands slider
            new Swiper('.brands-slider', {
                slidesPerView: 2,
                spaceBetween: 20,
                autoplay: {
                    delay: 3000,
                    disableOnInteraction: false,
                },
                loop: true,
                breakpoints: {
                    576: {
                        slidesPerView: 3,
                    },
                    768: {
                        slidesPerView: 4,
                    },
                    1024: {
                        slidesPerView: 6,
                    },
                }
            });
        },

        initBasicSliders: function() {
            // Basic slider implementation without external libraries
            this.createSimpleSlider('.product-slider');
        },

        createSimpleSlider: function(selector) {
            $(selector).each(function() {
                const $slider = $(this);
                const $items = $slider.find('.slider-item');
                const itemCount = $items.length;
                let currentIndex = 0;

                if (itemCount <= 1) return;

                // Create navigation
                $slider.append(`
                    <div class="slider-nav">
                        <button class="slider-prev"><i class="fa fa-chevron-left"></i></button>
                        <button class="slider-next"><i class="fa fa-chevron-right"></i></button>
                    </div>
                `);

                // Handle navigation clicks
                $slider.find('.slider-prev').on('click', function(e) {
                    e.preventDefault();
                    currentIndex = (currentIndex - 1 + itemCount) % itemCount;
                    updateSlider();
                });

                $slider.find('.slider-next').on('click', function(e) {
                    e.preventDefault();
                    currentIndex = (currentIndex + 1) % itemCount;
                    updateSlider();
                });

                function updateSlider() {
                    $items.removeClass('active').eq(currentIndex).addClass('active');
                }

                // Initialize first item
                $items.eq(0).addClass('active');
            });
        },

        initCounters: function() {
            // Initialize animated counters
            if ($('.counter').length > 0) {
                this.animateCounters();
            }
        },

        animateCounters: function() {
            $('.counter').each(function() {
                const $counter = $(this);
                const target = parseInt($counter.data('target'));
                const duration = parseInt($counter.data('duration')) || 2000;
                const increment = target / (duration / 16);
                let current = 0;

                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        current = target;
                        clearInterval(timer);
                    }
                    $counter.text(Math.floor(current));
                }, 16);
            });
        },

        initScrollAnimations: function() {
            // Initialize scroll-triggered animations
            if ('IntersectionObserver' in window) {
                this.initIntersectionObserver();
            } else {
                this.initScrollListener();
            }
        },

        initIntersectionObserver: function() {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        $(entry.target).addClass('animate-in');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '50px'
            });

            $('.animate-on-scroll').each(function() {
                observer.observe(this);
            });
        },

        initScrollListener: function() {
            // Fallback for browsers without IntersectionObserver
            $(window).on('scroll', this.debounce(() => {
                const scrollTop = $(window).scrollTop();
                const windowHeight = $(window).height();

                $('.animate-on-scroll:not(.animate-in)').each(function() {
                    const elementTop = $(this).offset().top;
                    if (elementTop < scrollTop + windowHeight - 100) {
                        $(this).addClass('animate-in');
                    }
                });
            }, 100));
        },

        animateHeroElements: function() {
            // Animate hero section elements on load
            setTimeout(() => {
                $('.hero-content h1').addClass('animate__animated animate__fadeInUp');
            }, 200);

            setTimeout(() => {
                $('.hero-content .lead').addClass('animate__animated animate__fadeInUp');
            }, 400);

            setTimeout(() => {
                $('.hero-content .btn').addClass('animate__animated animate__fadeInUp');
            }, 600);

            setTimeout(() => {
                $('.hero-image').addClass('animate__animated animate__fadeInRight');
            }, 800);
        },

        bindEvents: function() {
            // Newsletter subscription
            $(document).on('submit', '.newsletter-form', this.handleNewsletterSubmit.bind(this));

            // Category hover effects
            $(document).on('mouseenter', '.category-card', this.handleCategoryHover.bind(this));
            $(document).on('mouseleave', '.category-card', this.handleCategoryLeave.bind(this));

            // Product quick actions
            $(document).on('click', '.quick-add-btn', this.handleQuickAdd.bind(this));
            $(document).on('click', '.quick-view-btn', this.handleQuickView.bind(this));

            // Smooth scrolling for anchor links
            $(document).on('click', 'a[href^="#"]', this.handleSmoothScroll.bind(this));

            // Lazy loading for images
            if ('loading' in HTMLImageElement.prototype) {
                $('img[data-src]').each(function() {
                    this.src = this.dataset.src;
                    this.removeAttribute('data-src');
                });
            } else {
                this.initLazyLoading();
            }
        },

        handleNewsletterSubmit: function(e) {
            e.preventDefault();
            const $form = $(e.target);
            const $button = $form.find('button[type="submit"]');
            const email = $form.find('input[type="email"]').val();

            if (!this.validateEmail(email)) {
                this.showMessage('Please enter a valid email address', 'error');
                return;
            }

            $button.prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> Subscribing...');

            // Simulate newsletter subscription
            setTimeout(() => {
                this.showMessage('Thank you for subscribing to our newsletter!', 'success');
                $form[0].reset();
                $button.prop('disabled', false).text('Subscribe');
            }, 1500);
        },

        handleCategoryHover: function(e) {
            const $card = $(e.currentTarget);
            $card.find('.card-img-top img').addClass('scale-up');
        },

        handleCategoryLeave: function(e) {
            const $card = $(e.currentTarget);
            $card.find('.card-img-top img').removeClass('scale-up');
        },

        handleQuickAdd: function(e) {
            e.preventDefault();
            const $btn = $(e.target);
            const productId = $btn.data('product-id');

            // Show loading state
            $btn.addClass('loading').prop('disabled', true);

            // Simulate quick add (would normally make AJAX call)
            setTimeout(() => {
                $btn.removeClass('loading').prop('disabled', false);
                this.showMessage('Product added to cart!', 'success');
            }, 1000);
        },

        handleQuickView: function(e) {
            e.preventDefault();
            const $btn = $(e.target);
            const productId = $btn.data('product-id');

            // Would normally fetch product data and show modal
            this.showMessage('Quick view feature coming soon!', 'info');
        },

        handleSmoothScroll: function(e) {
            const target = $(e.target).attr('href');
            if (target && target !== '#' && $(target).length) {
                e.preventDefault();
                $('html, body').animate({
                    scrollTop: $(target).offset().top - 80
                }, 800);
            }
        },

        initLazyLoading: function() {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });

            $('img[data-src]').each(function() {
                imageObserver.observe(this);
            });
        },

        validateEmail: function(email) {
            const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return regex.test(email);
        },

        showMessage: function(message, type = 'info') {
            // Use global notification system if available
            if (typeof showNotification === 'function') {
                showNotification(message, type);
            } else {
                // Fallback notification
                const alertClass = type === 'error' ? 'danger' : type;
                const $alert = $(`
                    <div class="alert alert-${alertClass} alert-dismissible fade show position-fixed"
                         style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                        ${message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `);
                $('body').append($alert);

                setTimeout(() => {
                    $alert.alert('close');
                }, 5000);
            }
        },

        debounce: function(func, delay) {
            let timeoutId;
            return function (...args) {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => func.apply(this, args), delay);
            };
        }
    };

    // Testimonials functionality
    const Testimonials = {
        init: function() {
            if ($('.testimonials-slider').length > 0) {
                this.initSlider();
            }
        },

        initSlider: function() {
            if (typeof Swiper !== 'undefined') {
                new Swiper('.testimonials-slider', {
                    slidesPerView: 1,
                    spaceBetween: 30,
                    autoplay: {
                        delay: 5000,
                        disableOnInteraction: false,
                    },
                    navigation: {
                        nextEl: '.testimonials-next',
                        prevEl: '.testimonials-prev',
                    },
                    pagination: {
                        el: '.testimonials-pagination',
                        clickable: true,
                    },
                    breakpoints: {
                        768: {
                            slidesPerView: 2,
                        },
                        1024: {
                            slidesPerView: 3,
                        },
                    }
                });
            }
        }
    };

    // Initialize on document ready
    $(document).ready(function() {
        HomePage.init();
        Testimonials.init();
    });

    // Expose to global scope
    window.HomePage = HomePage;

})(jQuery);