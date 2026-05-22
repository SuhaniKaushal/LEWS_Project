/**
 * LEWS Navigation JavaScript
 * Version: 1.0.0
 *
 * Handles:
 * - Mobile hamburger menu with slide-in/slide-out
 * - Mega menu interactions
 * - Dropdown toggles (search, notifications, user)
 * - Sticky header on scroll
 * - Active page highlighting
 * - Breadcrumb generation
 * - Touch gestures for mobile
 * - Smooth scrolling
 */

(function() {
    'use strict';

    // ========================================================================
    // CONFIGURATION
    // ========================================================================

    const config = {
        scrollThreshold: 50,
        swipeThreshold: 50,
        touchStartX: 0,
        touchEndX: 0
    };

    // ========================================================================
    // DOM ELEMENTS
    // ========================================================================

    const elements = {
        nav: document.getElementById('mainNav'),
        mobileToggle: document.getElementById('mobileMenuToggle'),
        navMenu: document.getElementById('navMenu'),
        mobileOverlay: document.getElementById('mobileOverlay'),
        searchToggle: document.getElementById('searchToggle'),
        searchDropdown: document.getElementById('searchDropdown'),
        notificationToggle: document.getElementById('notificationToggle'),
        notificationDropdown: document.getElementById('notificationDropdown'),
        userToggle: document.getElementById('userToggle'),
        userDropdown: document.getElementById('userDropdown'),
        breadcrumbNav: document.getElementById('breadcrumbNav'),
        navLinks: document.querySelectorAll('.nav-link'),
        megaMenuItems: document.querySelectorAll('.has-mega-menu'),
        body: document.body
    };

    // ========================================================================
    // MOBILE MENU FUNCTIONALITY
    // ========================================================================

    /**
     * Toggle mobile menu open/close
     */
    function toggleMobileMenu() {
        const isExpanded = elements.mobileToggle.getAttribute('aria-expanded') === 'true';

        elements.mobileToggle.setAttribute('aria-expanded', !isExpanded);
        elements.navMenu.classList.toggle('active');
        elements.mobileOverlay.classList.toggle('active');
        elements.body.classList.toggle('menu-open');

        // Close all dropdowns when menu closes
        if (isExpanded) {
            closeAllDropdowns();
        }
    }

    /**
     * Close mobile menu
     */
    function closeMobileMenu() {
        elements.mobileToggle.setAttribute('aria-expanded', 'false');
        elements.navMenu.classList.remove('active');
        elements.mobileOverlay.classList.remove('active');
        elements.body.classList.remove('menu-open');
        closeAllDropdowns();
    }

    // ========================================================================
    // DROPDOWN FUNCTIONALITY
    // ========================================================================

    /**
     * Toggle dropdown visibility
     * @param {HTMLElement} toggle - The toggle button
     * @param {HTMLElement} dropdown - The dropdown element
     * @param {HTMLElement} parent - The parent container
     */
    function toggleDropdown(toggle, dropdown, parent) {
        const isActive = parent.classList.contains('active');

        // Close all other dropdowns first
        closeAllDropdowns();

        // Toggle current dropdown
        if (!isActive) {
            parent.classList.add('active');
            toggle.setAttribute('aria-expanded', 'true');
        }
    }

    /**
     * Close all dropdowns
     */
    function closeAllDropdowns() {
        // Search
        const searchParent = elements.searchToggle?.closest('.nav-search');
        if (searchParent) {
            searchParent.classList.remove('active');
            elements.searchToggle.setAttribute('aria-expanded', 'false');
        }

        // Notifications
        const notificationParent = elements.notificationToggle?.closest('.nav-notifications');
        if (notificationParent) {
            notificationParent.classList.remove('active');
            elements.notificationToggle.setAttribute('aria-expanded', 'false');
        }

        // User
        const userParent = elements.userToggle?.closest('.nav-user');
        if (userParent) {
            userParent.classList.remove('active');
            elements.userToggle.setAttribute('aria-expanded', 'false');
        }

        // Mega menus
        elements.megaMenuItems.forEach(item => {
            item.classList.remove('active');
            const link = item.querySelector('.nav-link');
            if (link) {
                link.setAttribute('aria-expanded', 'false');
            }
        });
    }

    // ========================================================================
    // STICKY HEADER ON SCROLL
    // ========================================================================

    /**
     * Handle scroll events for sticky header
     */
    function handleScroll() {
        if (window.scrollY > config.scrollThreshold) {
            elements.nav?.classList.add('scrolled');
        } else {
            elements.nav?.classList.remove('scrolled');
        }
    }

    // ========================================================================
    // ACTIVE PAGE HIGHLIGHTING
    // ========================================================================

    /**
     * Highlight active page in navigation
     */
    function highlightActivePage() {
        const currentPath = window.location.pathname;
        const currentHash = window.location.hash;

        elements.navLinks.forEach(link => {
            const linkPath = new URL(link.href).pathname;
            const linkHash = new URL(link.href).hash;

            // Exact match
            if (linkPath === currentPath && (!linkHash || linkHash === currentHash)) {
                link.classList.add('active');
            }
            // Partial match for sub-pages
            else if (currentPath.startsWith(linkPath) && linkPath !== '/') {
                link.classList.add('active');
            }
            // Check data-page attribute
            else if (link.dataset.page && currentPath.includes(link.dataset.page)) {
                link.classList.add('active');
            }
            else {
                link.classList.remove('active');
            }
        });
    }

    // ========================================================================
    // MEGA MENU FUNCTIONALITY
    // ========================================================================

    /**
     * Toggle mega menu on mobile
     * @param {HTMLElement} item - The mega menu item
     */
    function toggleMegaMenu(item) {
        const isMobile = window.innerWidth < 768;

        if (isMobile) {
            const isActive = item.classList.contains('active');

            // Close all mega menus
            elements.megaMenuItems.forEach(menuItem => {
                menuItem.classList.remove('active');
                const link = menuItem.querySelector('.nav-link');
                if (link) {
                    link.setAttribute('aria-expanded', 'false');
                }
            });

            // Toggle current mega menu
            if (!isActive) {
                item.classList.add('active');
                const link = item.querySelector('.nav-link');
                if (link) {
                    link.setAttribute('aria-expanded', 'true');
                }
            }
        }
    }

    // ========================================================================
    // BREADCRUMB GENERATION
    // ========================================================================

    /**
     * Generate breadcrumbs based on current page
     */
    function generateBreadcrumbs() {
        if (!elements.breadcrumbNav) return;

        const currentPath = window.location.pathname;
        const pathSegments = currentPath.split('/').filter(segment => segment);

        // Show breadcrumbs only on deep pages (more than 1 level)
        if (pathSegments.length > 1) {
            elements.breadcrumbNav.style.display = 'block';

            const breadcrumbList = elements.breadcrumbNav.querySelector('.breadcrumb');
            const activeItem = breadcrumbList.querySelector('.breadcrumb-item.active');

            if (activeItem) {
                // Get page title from document title or last segment
                const pageTitle = document.title.split('-')[0].trim() ||
                                pathSegments[pathSegments.length - 1].replace(/_/g, ' ');
                activeItem.textContent = pageTitle;
            }
        } else {
            elements.breadcrumbNav.style.display = 'none';
        }
    }

    // ========================================================================
    // TOUCH GESTURES (Mobile Swipe)
    // ========================================================================

    /**
     * Handle touch start
     * @param {TouchEvent} e - Touch event
     */
    function handleTouchStart(e) {
        config.touchStartX = e.changedTouches[0].screenX;
    }

    /**
     * Handle touch end
     * @param {TouchEvent} e - Touch event
     */
    function handleTouchEnd(e) {
        config.touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }

    /**
     * Detect swipe direction and handle accordingly
     */
    function handleSwipe() {
        const swipeDistance = config.touchEndX - config.touchStartX;

        // Swipe right to left (close menu)
        if (swipeDistance < -config.swipeThreshold && elements.navMenu.classList.contains('active')) {
            closeMobileMenu();
        }
    }

    // ========================================================================
    // SMOOTH SCROLL
    // ========================================================================

    /**
     * Handle smooth scrolling for anchor links
     * @param {Event} e - Click event
     */
    function handleSmoothScroll(e) {
        const link = e.target.closest('a');
        if (!link) return;

        const href = link.getAttribute('href');
        if (href && href.startsWith('#') && href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);

            if (target) {
                const offsetTop = target.offsetTop - 70; // Account for fixed nav height
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                if (window.innerWidth < 768) {
                    closeMobileMenu();
                }
            }
        }
    }

    // ========================================================================
    // NOTIFICATION ACTIONS
    // ========================================================================

    /**
     * Mark all notifications as read
     */
    function markAllNotificationsRead() {
        const notificationItems = document.querySelectorAll('.notification-item.unread');
        notificationItems.forEach(item => {
            item.classList.remove('unread');
        });

        // Update badge count
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            badge.textContent = '0';
            badge.style.display = 'none';
        }
    }

    // ========================================================================
    // CLICK OUTSIDE TO CLOSE
    // ========================================================================

    /**
     * Close dropdowns when clicking outside
     * @param {Event} e - Click event
     */
    function handleClickOutside(e) {
        // Don't close if clicking inside nav
        if (e.target.closest('.nav-search') ||
            e.target.closest('.nav-notifications') ||
            e.target.closest('.nav-user')) {
            return;
        }

        // Close all dropdowns
        closeAllDropdowns();
    }

    // ========================================================================
    // KEYBOARD NAVIGATION
    // ========================================================================

    /**
     * Handle keyboard events for accessibility
     * @param {KeyboardEvent} e - Keyboard event
     */
    function handleKeyboard(e) {
        // Escape key closes dropdowns and mobile menu
        if (e.key === 'Escape') {
            closeAllDropdowns();
            if (window.innerWidth < 768 && elements.navMenu.classList.contains('active')) {
                closeMobileMenu();
            }
        }
    }

    // ========================================================================
    // SEARCH FUNCTIONALITY
    // ========================================================================

    /**
     * Handle search form submission
     * @param {Event} e - Submit event
     */
    function handleSearchSubmit(e) {
        e.preventDefault();
        const searchInput = e.target.querySelector('.search-input');
        const query = searchInput.value.trim();

        if (query) {
            // Implement search logic here
            console.log('Searching for:', query);
            // Example: window.location.href = `/search?q=${encodeURIComponent(query)}`;
        }
    }

    // ========================================================================
    // WINDOW RESIZE HANDLER
    // ========================================================================

    /**
     * Handle window resize events
     */
    function handleResize() {
        // Close mobile menu when resizing to desktop
        if (window.innerWidth >= 768 && elements.navMenu.classList.contains('active')) {
            closeMobileMenu();
        }

        // Close mega menus on resize
        closeAllDropdowns();
    }

    // Debounce resize handler
    let resizeTimeout;
    function debouncedResize() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(handleResize, 250);
    }

    // ========================================================================
    // EVENT LISTENERS
    // ========================================================================

    /**
     * Initialize all event listeners
     */
    function initEventListeners() {
        // Mobile menu toggle
        elements.mobileToggle?.addEventListener('click', toggleMobileMenu);

        // Mobile overlay click closes menu
        elements.mobileOverlay?.addEventListener('click', closeMobileMenu);

        // Search toggle
        elements.searchToggle?.addEventListener('click', (e) => {
            e.stopPropagation();
            const parent = elements.searchToggle.closest('.nav-search');
            toggleDropdown(elements.searchToggle, elements.searchDropdown, parent);
        });

        // Notification toggle
        elements.notificationToggle?.addEventListener('click', (e) => {
            e.stopPropagation();
            const parent = elements.notificationToggle.closest('.nav-notifications');
            toggleDropdown(elements.notificationToggle, elements.notificationDropdown, parent);
        });

        // User toggle
        elements.userToggle?.addEventListener('click', (e) => {
            e.stopPropagation();
            const parent = elements.userToggle.closest('.nav-user');
            toggleDropdown(elements.userToggle, elements.userDropdown, parent);
        });

        // Mega menu toggle (mobile only)
        elements.megaMenuItems.forEach(item => {
            const link = item.querySelector('.nav-link');
            link?.addEventListener('click', (e) => {
                if (window.innerWidth < 768) {
                    e.preventDefault();
                    toggleMegaMenu(item);
                }
            });
        });

        // Mark all notifications as read
        const markAllReadBtn = document.querySelector('.mark-all-read');
        markAllReadBtn?.addEventListener('click', markAllNotificationsRead);

        // Search form submission
        const searchForm = document.querySelector('.search-form');
        searchForm?.addEventListener('submit', handleSearchSubmit);

        // Smooth scroll for anchor links
        document.addEventListener('click', handleSmoothScroll);

        // Close dropdowns when clicking outside
        document.addEventListener('click', handleClickOutside);

        // Keyboard navigation
        document.addEventListener('keydown', handleKeyboard);

        // Scroll events
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(handleScroll, 10);
        }, { passive: true });

        // Touch events for swipe gestures
        if (elements.navMenu) {
            elements.navMenu.addEventListener('touchstart', handleTouchStart, { passive: true });
            elements.navMenu.addEventListener('touchend', handleTouchEnd, { passive: true });
        }

        // Window resize
        window.addEventListener('resize', debouncedResize);
    }

    // ========================================================================
    // INITIALIZATION
    // ========================================================================

    /**
     * Initialize navigation functionality
     */
    function init() {
        // Set up event listeners
        initEventListeners();

        // Highlight active page
        highlightActivePage();

        // Generate breadcrumbs
        generateBreadcrumbs();

        // Initial scroll check
        handleScroll();

        console.log('LEWS Navigation initialized');
    }

    // ========================================================================
    // AUTO-INITIALIZE ON DOM READY
    // ========================================================================

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // ========================================================================
    // PUBLIC API (optional - for external access)
    // ========================================================================

    window.LEWSNav = {
        closeMobileMenu,
        closeAllDropdowns,
        highlightActivePage,
        generateBreadcrumbs
    };

})();
