/**
 * LEWS Interactive Elements
 * Modern interactions and microanimations
 * Version: 1.0.0
 */

(function($) {
    'use strict';

    // ========================================================================
    // INITIALIZATION
    // ========================================================================

    $(document).ready(function() {
        initScrollAnimations();
        initTooltips();
        initPopovers();
        initModals();
        initDropdowns();
        initTabs();
        initAccordions();
        initFormValidation();
        initMicrointeractions();
        initCustomScrollbars();
        initParallax();
        initLazyLoading();
        initNotifications();
        initCharts();
    });

    // ========================================================================
    // SCROLL ANIMATIONS
    // ========================================================================

    function initScrollAnimations() {
        const scrollElements = document.querySelectorAll('.scroll-fade-in, .scroll-scale-in');

        const elementInView = (el, offset = 100) => {
            const elementTop = el.getBoundingClientRect().top;
            return elementTop <= (window.innerHeight || document.documentElement.clientHeight) - offset;
        };

        const displayScrollElement = (element) => {
            element.classList.add('visible');
        };

        const hideScrollElement = (element) => {
            element.classList.remove('visible');
        };

        const handleScrollAnimation = () => {
            scrollElements.forEach((el) => {
                if (elementInView(el, 100)) {
                    displayScrollElement(el);
                }
            });
        };

        window.addEventListener('scroll', () => {
            handleScrollAnimation();
        });

        // Initial check
        handleScrollAnimation();
    }

    // ========================================================================
    // TOOLTIPS
    // ========================================================================

    function initTooltips() {
        // Bootstrap 5 Tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                trigger: 'hover',
                animation: true,
                delay: { show: 200, hide: 100 }
            });
        });

        // Custom tooltip for sensor data
        $('.sensor-value[data-tooltip]').hover(
            function() {
                const tooltipText = $(this).data('tooltip');
                const $tooltip = $('<div class="custom-tooltip"></div>').text(tooltipText);
                $('body').append($tooltip);

                const offset = $(this).offset();
                $tooltip.css({
                    top: offset.top - $tooltip.outerHeight() - 10,
                    left: offset.left + ($(this).outerWidth() / 2) - ($tooltip.outerWidth() / 2)
                }).addClass('fade-in');
            },
            function() {
                $('.custom-tooltip').remove();
            }
        );
    }

    // ========================================================================
    // POPOVERS
    // ========================================================================

    function initPopovers() {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl, {
                trigger: 'click',
                html: true,
                animation: true,
                customClass: 'custom-popover'
            });
        });

        // Sensor detail popover
        $('.sensor-card').on('click', '.info-icon', function(e) {
            e.stopPropagation();
            const sensorId = $(this).closest('.sensor-card').data('sensor-id');
            showSensorDetailPopover($(this), sensorId);
        });
    }

    function showSensorDetailPopover($element, sensorId) {
        const content = `
            <div class="sensor-detail-popover">
                <h6>Sensor ${sensorId}</h6>
                <p class="mb-1"><strong>Status:</strong> Active</p>
                <p class="mb-1"><strong>Last Reading:</strong> 2 mins ago</p>
                <p class="mb-1"><strong>Location:</strong> Site A</p>
                <button class="btn btn-sm btn-primary mt-2">View Details</button>
            </div>
        `;

        new bootstrap.Popover($element[0], {
            content: content,
            html: true,
            placement: 'right',
            trigger: 'focus'
        }).show();
    }

    // ========================================================================
    // MODALS
    // ========================================================================

    function initModals() {
        // Sensor Details Modal
        $(document).on('click', '.view-sensor-details', function(e) {
            e.preventDefault();
            const sensorId = $(this).data('sensor-id');
            showSensorModal(sensorId);
        });

        // Alert Acknowledgment Modal
        $(document).on('click', '.acknowledge-alert', function(e) {
            e.preventDefault();
            const alertId = $(this).data('alert-id');
            showAlertAcknowledgeModal(alertId);
        });

        // Data Export Modal
        $(document).on('click', '.export-data-btn', function(e) {
            e.preventDefault();
            showDataExportModal();
        });

        // User Settings Modal
        $(document).on('click', '.user-settings-btn', function(e) {
            e.preventDefault();
            showUserSettingsModal();
        });

        // Add modal backdrop animation
        $(document).on('show.bs.modal', '.modal', function() {
            $(this).find('.modal-dialog').addClass('modal-slide-down');
        });
    }

    function showSensorModal(sensorId) {
        const modalHTML = `
            <div class="modal fade" id="sensorModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-microchip me-2"></i>Sensor Details - ${sensorId}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Current Status</h6>
                                    <p><span class="badge bg-success">Active</span></p>
                                    <h6>Last Reading</h6>
                                    <p>2 minutes ago</p>
                                    <h6>Location</h6>
                                    <p>Site A, Zone 3</p>
                                </div>
                                <div class="col-md-6">
                                    <h6>Recent Data</h6>
                                    <canvas id="sensorChart"></canvas>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-primary">Download Report</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        $('body').append(modalHTML);
        const modal = new bootstrap.Modal(document.getElementById('sensorModal'));
        modal.show();

        $('#sensorModal').on('hidden.bs.modal', function() {
            $(this).remove();
        });
    }

    function showAlertAcknowledgeModal(alertId) {
        const modalHTML = `
            <div class="modal fade" id="alertAckModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header bg-warning">
                            <h5 class="modal-title">
                                <i class="fas fa-exclamation-triangle me-2"></i>Acknowledge Alert
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>Are you sure you want to acknowledge this alert?</p>
                            <textarea class="form-control" rows="3" placeholder="Add notes (optional)"></textarea>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-warning" onclick="acknowledgeAlert('${alertId}')">
                                Acknowledge
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        $('body').append(modalHTML);
        const modal = new bootstrap.Modal(document.getElementById('alertAckModal'));
        modal.show();

        $('#alertAckModal').on('hidden.bs.modal', function() {
            $(this).remove();
        });
    }

    function showDataExportModal() {
        const modalHTML = `
            <div class="modal fade" id="dataExportModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-download me-2"></i>Export Data
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">Export Format</label>
                                <select class="form-select">
                                    <option value="csv">CSV</option>
                                    <option value="excel">Excel (XLSX)</option>
                                    <option value="json">JSON</option>
                                    <option value="pdf">PDF Report</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Date Range</label>
                                <input type="text" class="form-control daterange-picker" placeholder="Select date range">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Include</label>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" checked>
                                    <label class="form-check-label">Sensor Readings</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox">
                                    <label class="form-check-label">Alert History</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox">
                                    <label class="form-check-label">Summary Statistics</label>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="exportData()">
                                <i class="fas fa-download me-2"></i>Export
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        $('body').append(modalHTML);
        const modal = new bootstrap.Modal(document.getElementById('dataExportModal'));
        modal.show();

        $('#dataExportModal').on('hidden.bs.modal', function() {
            $(this).remove();
        });
    }

    function showUserSettingsModal() {
        const modalHTML = `
            <div class="modal fade" id="userSettingsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-cog me-2"></i>User Settings
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <ul class="nav nav-tabs mb-3" role="tablist">
                                <li class="nav-item">
                                    <a class="nav-link active" data-bs-toggle="tab" href="#profileTab">Profile</a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" data-bs-toggle="tab" href="#notificationsTab">Notifications</a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" data-bs-toggle="tab" href="#preferencesTab">Preferences</a>
                                </li>
                            </ul>
                            <div class="tab-content">
                                <div class="tab-pane fade show active" id="profileTab">
                                    <h6>Profile Information</h6>
                                    <p>Update your profile details here.</p>
                                </div>
                                <div class="tab-pane fade" id="notificationsTab">
                                    <h6>Notification Settings</h6>
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" checked>
                                        <label class="form-check-label">Email Notifications</label>
                                    </div>
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" checked>
                                        <label class="form-check-label">Alert Notifications</label>
                                    </div>
                                </div>
                                <div class="tab-pane fade" id="preferencesTab">
                                    <h6>Display Preferences</h6>
                                    <p>Customize your dashboard view.</p>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary">Save Changes</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        $('body').append(modalHTML);
        const modal = new bootstrap.Modal(document.getElementById('userSettingsModal'));
        modal.show();

        $('#userSettingsModal').on('hidden.bs.modal', function() {
            $(this).remove();
        });
    }

    // ========================================================================
    // DROPDOWNS
    // ========================================================================

    function initDropdowns() {
        // Add smooth transition to dropdowns
        $('.dropdown-menu').on('show.bs.dropdown', function() {
            $(this).addClass('dropdown-slide');
        });

        // Custom dropdown interactions
        $('.custom-dropdown-toggle').click(function(e) {
            e.preventDefault();
            $(this).next('.custom-dropdown-menu').slideToggle(200).addClass('dropdown-slide');
        });

        // Close dropdown when clicking outside
        $(document).click(function(e) {
            if (!$(e.target).closest('.custom-dropdown').length) {
                $('.custom-dropdown-menu').slideUp(200);
            }
        });
    }

    // ========================================================================
    // TABS
    // ========================================================================

    function initTabs() {
        // Add animation to tab content
        $('a[data-bs-toggle="tab"]').on('shown.bs.tab', function(e) {
            $($(e.target).attr('href')).addClass('tab-fade-in');
        });

        // Custom tab switching with animation
        $('.custom-tab-link').click(function(e) {
            e.preventDefault();
            const targetTab = $(this).data('target');

            $('.custom-tab-link').removeClass('active');
            $(this).addClass('active');

            $('.custom-tab-pane').removeClass('active').hide();
            $(targetTab).fadeIn(300).addClass('active tab-fade-in');
        });
    }

    // ========================================================================
    // ACCORDIONS
    // ========================================================================

    function initAccordions() {
        // Bootstrap 5 accordion smooth animation is handled by CSS

        // Custom accordion implementation
        $('.custom-accordion-header').click(function() {
            const $content = $(this).next('.custom-accordion-content');
            const $icon = $(this).find('.accordion-icon');

            if ($content.is(':visible')) {
                $content.slideUp(250);
                $icon.removeClass('fa-chevron-up').addClass('fa-chevron-down');
            } else {
                $('.custom-accordion-content').slideUp(250);
                $('.accordion-icon').removeClass('fa-chevron-up').addClass('fa-chevron-down');

                $content.slideDown(250);
                $icon.removeClass('fa-chevron-down').addClass('fa-chevron-up');
            }
        });
    }

    // ========================================================================
    // FORM VALIDATION
    // ========================================================================

    function initFormValidation() {
        // Real-time validation
        $('input[required], textarea[required], select[required]').on('blur', function() {
            validateField($(this));
        });

        // Form submission
        $('form[data-validate]').on('submit', function(e) {
            e.preventDefault();

            let isValid = true;
            $(this).find('input[required], textarea[required], select[required]').each(function() {
                if (!validateField($(this))) {
                    isValid = false;
                }
            });

            if (isValid) {
                showSuccessAnimation($(this));
                // Submit form
                // this.submit();
            } else {
                $(this).addClass('error-shake');
                setTimeout(() => $(this).removeClass('error-shake'), 500);
            }
        });
    }

    function validateField($field) {
        const value = $field.val().trim();
        const fieldType = $field.attr('type');
        let isValid = true;

        // Remove previous feedback
        $field.removeClass('is-invalid is-valid');
        $field.next('.invalid-feedback').remove();

        if (!value) {
            isValid = false;
            showFieldError($field, 'This field is required');
        } else if (fieldType === 'email' && !isValidEmail(value)) {
            isValid = false;
            showFieldError($field, 'Please enter a valid email address');
        }

        if (isValid) {
            $field.addClass('is-valid');
        }

        return isValid;
    }

    function showFieldError($field, message) {
        $field.addClass('is-invalid error-shake');
        $field.after(`<div class="invalid-feedback">${message}</div>`);
        setTimeout(() => $field.removeClass('error-shake'), 500);
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function showSuccessAnimation($form) {
        const $checkmark = $('<div class="success-checkmark"><svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52"><circle class="checkmark-circle" cx="26" cy="26" r="25" fill="none"/><path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/></svg></div>');

        $form.append($checkmark);

        setTimeout(() => {
            $checkmark.fadeOut(300, function() {
                $(this).remove();
            });
        }, 2000);
    }

    // ========================================================================
    // MICROINTERACTIONS
    // ========================================================================

    function initMicrointeractions() {
        // Copy to clipboard
        $('.copy-to-clipboard').click(function(e) {
            e.preventDefault();
            const text = $(this).data('copy-text');

            navigator.clipboard.writeText(text).then(() => {
                $(this).addClass('copy-flash');
                showNotification('Copied to clipboard!', 'success');

                setTimeout(() => {
                    $(this).removeClass('copy-flash');
                }, 500);
            });
        });

        // Toggle switches
        $('.toggle-switch input').change(function() {
            const $switch = $(this).closest('.toggle-switch');

            if ($(this).is(':checked')) {
                $switch.addClass('active');
            } else {
                $switch.removeClass('active');
            }
        });

        // Number counter animation
        $('.counter').each(function() {
            const $this = $(this);
            const countTo = parseInt($this.text());

            $({ countNum: 0 }).animate({
                countNum: countTo
            }, {
                duration: 2000,
                easing: 'swing',
                step: function() {
                    $this.text(Math.floor(this.countNum));
                },
                complete: function() {
                    $this.text(this.countNum);
                }
            });
        });

        // Button ripple effect
        $('.btn-ripple').click(function(e) {
            const $ripple = $('<span class="ripple"></span>');
            const diameter = Math.max($(this).width(), $(this).height());
            const radius = diameter / 2;

            $ripple.css({
                width: diameter,
                height: diameter,
                left: e.pageX - $(this).offset().left - radius,
                top: e.pageY - $(this).offset().top - radius
            });

            $(this).append($ripple);

            setTimeout(() => {
                $ripple.remove();
            }, 600);
        });

        // Card click animation
        $('.card-clickable').click(function() {
            $(this).addClass('card-clicked');
            setTimeout(() => {
                $(this).removeClass('card-clicked');
            }, 300);
        });

        // Loading state for buttons
        $('.btn-loading').click(function() {
            const $btn = $(this);
            const originalText = $btn.html();

            $btn.prop('disabled', true)
                .html('<span class="spinner-border spinner-border-sm me-2"></span>Loading...');

            // Simulate async operation
            setTimeout(() => {
                $btn.prop('disabled', false).html(originalText);
            }, 2000);
        });
    }

    // ========================================================================
    // CUSTOM SCROLLBARS
    // ========================================================================

    function initCustomScrollbars() {
        // For elements with custom scrollbar
        if (typeof SimpleBar !== 'undefined') {
            document.querySelectorAll('.custom-scrollbar').forEach(el => {
                new SimpleBar(el);
            });
        }
    }

    // ========================================================================
    // PARALLAX EFFECT
    // ========================================================================

    function initParallax() {
        $(window).on('scroll', function() {
            const scrolled = $(this).scrollTop();

            $('.parallax-slow').css('transform', `translateY(${scrolled * 0.3}px)`);
            $('.parallax-medium').css('transform', `translateY(${scrolled * 0.5}px)`);
            $('.parallax-fast').css('transform', `translateY(${scrolled * 0.7}px)`);
        });
    }

    // ========================================================================
    // LAZY LOADING
    // ========================================================================

    function initLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.add('fade-in');
                        imageObserver.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    // ========================================================================
    // NOTIFICATIONS
    // ========================================================================

    function showNotification(message, type = 'info', duration = 3000) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        const notification = $(`
            <div class="custom-notification notification-${type} notification-slide-in">
                <i class="fas ${icons[type]} me-2"></i>
                <span>${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `);

        $('#notificationContainer').append(notification);

        setTimeout(() => {
            notification.addClass('notification-slide-out');
            setTimeout(() => notification.remove(), 300);
        }, duration);

        notification.find('.notification-close').click(function() {
            notification.addClass('notification-slide-out');
            setTimeout(() => notification.remove(), 300);
        });
    }

    // Initialize notification container
    if (!$('#notificationContainer').length) {
        $('body').append('<div id="notificationContainer" style="position: fixed; top: 80px; right: 20px; z-index: 9999;"></div>');
    }

    // ========================================================================
    // CHARTS
    // ========================================================================

    function initCharts() {
        // Add animation to charts when they come into view
        const chartObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    $(entry.target).addClass('chart-animate');
                }
            });
        });

        document.querySelectorAll('canvas[data-chart]').forEach(chart => {
            chartObserver.observe(chart);
        });
    }

    // ========================================================================
    // GLOBAL FUNCTIONS
    // ========================================================================

    window.acknowledgeAlert = function(alertId) {
        showNotification('Alert acknowledged successfully', 'success');
        bootstrap.Modal.getInstance(document.getElementById('alertAckModal')).hide();
    };

    window.exportData = function() {
        showNotification('Preparing export...', 'info');

        // Simulate export process
        setTimeout(() => {
            showNotification('Export completed successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('dataExportModal')).hide();
        }, 2000);
    };

    window.showNotification = showNotification;

})(jQuery);
