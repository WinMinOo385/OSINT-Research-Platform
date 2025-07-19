/**
 * OSINT Research Platform - Main JavaScript
 * Handles general UI interactions, form validations, and common functionality
 */

// Global app object
const OSINTApp = {
    // Configuration
    config: {
        apiBase: '/api',
        chartColors: {
            primary: '#1B263B',
            secondary: '#415A77',
            accent: '#778DA9',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#D62828',
            info: '#17a2b8'
        }
    },

    // Initialize the application
    init: function() {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupFormValidations();
        console.log('OSINT Platform initialized');
    },

    // Set up global event listeners
    setupEventListeners: function() {
        // Global form submission handlers
        document.addEventListener('submit', this.handleFormSubmission.bind(this));
        
        // Global click handlers
        document.addEventListener('click', this.handleGlobalClicks.bind(this));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));
        
        // Window resize handler for responsive charts
        window.addEventListener('resize', this.handleWindowResize.bind(this));
        
        // Page visibility API for pausing/resuming data updates
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
    },

    // Initialize UI components
    initializeComponents: function() {
        // Initialize tooltips
        this.initializeTooltips();
        
        // Initialize modals
        this.initializeModals();
        
        // Initialize data tables
        this.initializeDataTables();
        
        // Initialize progress indicators
        this.initializeProgressIndicators();
        
        // Initialize clipboard functionality
        this.initializeClipboard();
    },

    // Form validation setup
    setupFormValidations: function() {
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            this.addFormValidation(form);
        });
    },

    // Handle form submissions with loading states
    handleFormSubmission: function(event) {
        const form = event.target;
        
        if (form.classList.contains('ajax-form')) {
            event.preventDefault();
            this.submitFormAjax(form);
            return;
        }
        
        // Add loading state to submit button
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
            this.setButtonLoading(submitBtn, true);
        }
    },

    // Handle global click events
    handleGlobalClicks: function(event) {
        const target = event.target.closest('[data-action]');
        if (!target) return;

        const action = target.dataset.action;
        const params = target.dataset.params ? JSON.parse(target.dataset.params) : {};

        switch (action) {
            case 'copy-text':
                this.copyToClipboard(params.text || target.textContent);
                break;
            case 'toggle-section':
                this.toggleSection(params.target);
                break;
            case 'confirm-action':
                this.confirmAction(target, params);
                break;
            case 'export-data':
                this.exportData(params);
                break;
            default:
                console.warn('Unknown action:', action);
        }
    },

    // Keyboard shortcuts
    handleKeyboardShortcuts: function(event) {
        // Ctrl/Cmd + K for search
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            const searchInput = document.querySelector('#target');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals
        if (event.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modalInstance = bootstrap.Modal.getInstance(openModal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        }
    },

    // Window resize handler
    handleWindowResize: function() {
        // Debounce resize events
        clearTimeout(this.resizeTimeout);
        this.resizeTimeout = setTimeout(() => {
            // Trigger chart resize if charts exist
            if (window.dashboardCharts) {
                Object.values(window.dashboardCharts).forEach(chart => {
                    if (chart && typeof chart.resize === 'function') {
                        chart.resize();
                    }
                });
            }
        }, 250);
    },

    // Page visibility change handler
    handleVisibilityChange: function() {
        if (document.hidden) {
            // Page is hidden - pause any auto-refresh timers
            console.log('Page hidden - pausing updates');
        } else {
            // Page is visible - resume updates
            console.log('Page visible - resuming updates');
        }
    },

    // Initialize tooltips
    initializeTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    // Initialize modals
    initializeModals: function() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('show.bs.modal', this.handleModalShow.bind(this));
            modal.addEventListener('hidden.bs.modal', this.handleModalHidden.bind(this));
        });
    },

    // Modal event handlers
    handleModalShow: function(event) {
        const modal = event.target;
        const firstInput = modal.querySelector('input:not([type="hidden"]), textarea, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    },

    handleModalHidden: function(event) {
        const modal = event.target;
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
            this.clearFormErrors(form);
        }
    },

    // Initialize data tables with sorting and filtering
    initializeDataTables: function() {
        const tables = document.querySelectorAll('.data-table');
        tables.forEach(table => {
            this.enhanceTable(table);
        });
    },

    // Enhance table with sorting and filtering
    enhanceTable: function(table) {
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => this.sortTable(table, header));
        });
    },

    // Table sorting functionality
    sortTable: function(table, header) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const column = Array.from(header.parentNode.children).indexOf(header);
        const currentSort = header.dataset.sort || 'none';
        
        // Determine new sort direction
        let newSort = 'asc';
        if (currentSort === 'asc') newSort = 'desc';
        else if (currentSort === 'desc') newSort = 'none';
        
        // Clear all sort indicators
        table.querySelectorAll('th[data-sortable]').forEach(th => {
            th.dataset.sort = 'none';
            th.classList.remove('sort-asc', 'sort-desc');
        });
        
        if (newSort !== 'none') {
            header.dataset.sort = newSort;
            header.classList.add(`sort-${newSort}`);
            
            // Sort rows
            rows.sort((a, b) => {
                const aVal = a.children[column].textContent.trim();
                const bVal = b.children[column].textContent.trim();
                
                // Try to parse as numbers
                const aNum = parseFloat(aVal);
                const bNum = parseFloat(bVal);
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return newSort === 'asc' ? aNum - bNum : bNum - aNum;
                }
                
                // Sort as strings
                return newSort === 'asc' ? 
                    aVal.localeCompare(bVal) : 
                    bVal.localeCompare(aVal);
            });
            
            // Reorder DOM
            rows.forEach(row => tbody.appendChild(row));
        }
    },

    // Initialize progress indicators
    initializeProgressIndicators: function() {
        const progressBars = document.querySelectorAll('.progress-bar[data-animate]');
        progressBars.forEach(bar => {
            const targetWidth = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = targetWidth;
            }, 100);
        });
    },

    // Initialize clipboard functionality
    initializeClipboard: function() {
        // Add copy buttons to code blocks
        const codeBlocks = document.querySelectorAll('pre code, pre');
        codeBlocks.forEach(block => {
            if (!block.querySelector('.copy-btn')) {
                const copyBtn = document.createElement('button');
                copyBtn.className = 'btn btn-sm btn-outline-secondary copy-btn';
                copyBtn.innerHTML = '<i data-feather="copy"></i>';
                copyBtn.style.position = 'absolute';
                copyBtn.style.top = '0.5rem';
                copyBtn.style.right = '0.5rem';
                copyBtn.addEventListener('click', () => {
                    this.copyToClipboard(block.textContent);
                });
                
                block.style.position = 'relative';
                block.appendChild(copyBtn);
                feather.replace();
            }
        });
    },

    // Copy text to clipboard
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                this.showNotification('Copied to clipboard', 'success');
            }).catch(err => {
                console.error('Failed to copy: ', err);
                this.showNotification('Failed to copy to clipboard', 'danger');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                this.showNotification('Copied to clipboard', 'success');
            } catch (err) {
                console.error('Failed to copy: ', err);
                this.showNotification('Failed to copy to clipboard', 'danger');
            }
            document.body.removeChild(textArea);
        }
    },

    // Toggle section visibility
    toggleSection: function(targetSelector) {
        const target = document.querySelector(targetSelector);
        if (target) {
            target.classList.toggle('d-none');
        }
    },

    // Confirm action dialog
    confirmAction: function(element, params) {
        const message = params.message || 'Are you sure you want to perform this action?';
        const confirmText = params.confirmText || 'Confirm';
        const cancelText = params.cancelText || 'Cancel';
        
        if (confirm(message)) {
            if (params.href) {
                window.location.href = params.href;
            } else if (params.form) {
                const form = document.querySelector(params.form);
                if (form) form.submit();
            }
        }
    },

    // Form validation
    addFormValidation: function(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    },

    // Validate individual field
    validateField: function(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        let isValid = true;
        let errorMessage = '';

        // Required field validation
        if (required && !value) {
            isValid = false;
            errorMessage = 'This field is required.';
        }

        // Email validation
        if (type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address.';
            }
        }

        // URL validation
        if (type === 'url' && value) {
            try {
                new URL(value);
            } catch {
                isValid = false;
                errorMessage = 'Please enter a valid URL.';
            }
        }

        // Custom validation patterns
        if (field.hasAttribute('pattern') && value) {
            const pattern = new RegExp(field.getAttribute('pattern'));
            if (!pattern.test(value)) {
                isValid = false;
                errorMessage = field.getAttribute('data-error-message') || 'Invalid format.';
            }
        }

        this.setFieldValidation(field, isValid, errorMessage);
        return isValid;
    },

    // Set field validation state
    setFieldValidation: function(field, isValid, errorMessage) {
        field.classList.remove('is-valid', 'is-invalid');
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        if (isValid) {
            field.classList.add('is-valid');
        } else {
            field.classList.add('is-invalid');
            
            // Add error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = errorMessage;
            field.parentNode.appendChild(errorDiv);
        }
    },

    // Clear field error
    clearFieldError: function(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    },

    // Clear all form errors
    clearFormErrors: function(form) {
        const invalidFields = form.querySelectorAll('.is-invalid');
        invalidFields.forEach(field => this.clearFieldError(field));
    },

    // Set button loading state
    setButtonLoading: function(button, loading) {
        if (loading) {
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<div class="spinner-border spinner-border-sm me-2"></div>Loading...';
            button.disabled = true;
        } else {
            button.innerHTML = button.dataset.originalText || button.innerHTML;
            button.disabled = false;
        }
    },

    // AJAX form submission
    submitFormAjax: function(form) {
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        this.setButtonLoading(submitBtn, true);

        fetch(form.action, {
            method: form.method,
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification(data.message || 'Operation completed successfully', 'success');
                if (data.redirect) {
                    window.location.href = data.redirect;
                }
            } else {
                this.showNotification(data.message || 'Operation failed', 'danger');
                if (data.errors) {
                    this.displayFormErrors(form, data.errors);
                }
            }
        })
        .catch(error => {
            console.error('Form submission error:', error);
            this.showNotification('An error occurred. Please try again.', 'danger');
        })
        .finally(() => {
            this.setButtonLoading(submitBtn, false);
        });
    },

    // Display form errors
    displayFormErrors: function(form, errors) {
        Object.keys(errors).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                this.setFieldValidation(field, false, errors[fieldName]);
            }
        });
    },

    // Show notification
    showNotification: function(message, type = 'info', duration = 3000) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification`;
        notification.innerHTML = `
            <i data-feather="${this.getNotificationIcon(type)}" class="me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Add to page
        const container = document.querySelector('.notification-container') || document.body;
        container.appendChild(notification);
        
        // Replace feather icons
        feather.replace();
        
        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 150);
            }, duration);
        }
    },

    // Get notification icon based on type
    getNotificationIcon: function(type) {
        const icons = {
            success: 'check-circle',
            danger: 'x-circle',
            warning: 'alert-triangle',
            info: 'info'
        };
        return icons[type] || 'info';
    },

    // Format numbers with commas
    formatNumber: function(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },

    // Format dates
    formatDate: function(date, format = 'short') {
        const d = new Date(date);
        const options = {
            short: { year: 'numeric', month: 'short', day: 'numeric' },
            long: { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' },
            time: { hour: '2-digit', minute: '2-digit' }
        };
        return d.toLocaleDateString('en-US', options[format]);
    },

    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Throttle function
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    OSINTApp.init();
});

// Export for use in other modules
window.OSINTApp = OSINTApp;
