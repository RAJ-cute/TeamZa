/* Main JavaScript file for AI-Powered HR Platform */

// Global application state
const HRPlatform = {
    currentModule: '',
    notifications: [],
    user: null,
    config: {
        animationDuration: 300,
        chartColors: ['#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1', '#20c997'],
        apiTimeout: 30000
    }
};

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApplication();
    setupEventListeners();
    initializeTooltips();
    checkNotifications();
});

/**
 * Initialize the application
 */
function initializeApplication() {
    console.log('Initializing HR Platform...');
    
    // Set current module based on URL
    const path = window.location.pathname;
    HRPlatform.currentModule = getModuleFromPath(path);
    
    // Update active navigation
    updateActiveNavigation();
    
    // Initialize any charts on the current page
    initializeChartsOnPage();
    
    // Setup form validations
    setupFormValidations();
    
    console.log(`HR Platform initialized. Current module: ${HRPlatform.currentModule}`);
}

/**
 * Setup global event listeners
 */
function setupEventListeners() {
    // Handle navigation clicks
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.startsWith('/')) {
                showLoadingState();
            }
        });
    });
    
    // Handle form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!this.classList.contains('no-validation')) {
                if (!validateForm(this)) {
                    e.preventDefault();
                    showNotification('Please fix the errors in the form', 'error');
                    return false;
                }
            }
            
            showLoadingState();
        });
    });
    
    // Handle file uploads
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.addEventListener('change', function(e) {
            handleFileUpload(e);
        });
    });
    
    // Handle card hover effects
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Handle range input updates
    document.querySelectorAll('input[type="range"]').forEach(range => {
        range.addEventListener('input', function() {
            updateRangeDisplay(this);
        });
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Get module name from URL path
 */
function getModuleFromPath(path) {
    const moduleMap = {
        '/': 'dashboard',
        '/resume-screening': 'resume_screening',
        '/talent-sourcing': 'talent_sourcing',
        '/leadership-potential': 'leadership_potential',
        '/appraisal-dashboard': 'appraisal_dashboard',
        '/learning-module': 'learning_module',
        '/skill-gap-analysis': 'skill_gap_analysis',
        '/wellness-tracker': 'wellness_tracker',
        '/hr-insights': 'hr_insights'
    };
    
    return moduleMap[path] || 'unknown';
}

/**
 * Update active navigation item
 */
function updateActiveNavigation() {
    const currentPath = window.location.pathname;
    
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

/**
 * Show loading state
 */
function showLoadingState() {
    const loadingHtml = `
        <div class="d-flex justify-content-center align-items-center" style="min-height: 200px;">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <span class="ms-3">Loading...</span>
        </div>
    `;
    
    // You can customize this to show loading on specific elements
    console.log('Loading state activated');
}

/**
 * Handle file uploads
 */
function handleFileUpload(event) {
    const files = event.target.files;
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['text/plain', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    
    for (let file of files) {
        if (file.size > maxSize) {
            showNotification(`File ${file.name} is too large. Maximum size is 10MB.`, 'error');
            event.target.value = '';
            return false;
        }
        
        if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.txt')) {
            showNotification(`File ${file.name} has an unsupported format.`, 'error');
            event.target.value = '';
            return false;
        }
    }
    
    if (files.length > 0) {
        showNotification(`${files.length} file(s) selected successfully`, 'success');
    }
}

/**
 * Validate form fields
 */
function validateForm(form) {
    let isValid = true;
    
    // Remove existing error classes
    form.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });
    
    // Validate required fields
    form.querySelectorAll('[required]').forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    // Validate email fields
    form.querySelectorAll('input[type="email"]').forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    // Validate file uploads
    form.querySelectorAll('input[type="file"][required]').forEach(field => {
        if (field.files.length === 0) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Update range input display
 */
function updateRangeDisplay(rangeInput) {
    const value = rangeInput.value;
    const displayId = rangeInput.id.replace('_level', '_value').replace('_quality', '_value');
    const displayElement = document.getElementById(displayId);
    
    if (displayElement) {
        displayElement.textContent = value;
    }
    
    // Update color based on value
    if (rangeInput.id.includes('stress')) {
        // Higher stress = more red
        const intensity = (value - 1) / 9;
        rangeInput.style.background = `linear-gradient(to right, #28a745 0%, #ffc107 50%, #dc3545 100%)`;
    } else {
        // Higher value = more green
        const intensity = (value - 1) / 9;
        rangeInput.style.background = `linear-gradient(to right, #dc3545 0%, #ffc107 50%, #28a745 100%)`;
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info', duration = 5000) {
    const notificationId = 'notification-' + Date.now();
    const alertClass = type === 'error' ? 'danger' : type;
    
    const notificationHtml = `
        <div id="${notificationId}" class="alert alert-${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 1050; max-width: 400px;" role="alert">
            <strong>${type.charAt(0).toUpperCase() + type.slice(1)}:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', notificationHtml);
    
    // Auto-remove after duration
    setTimeout(() => {
        const notification = document.getElementById(notificationId);
        if (notification) {
            notification.remove();
        }
    }, duration);
}

/**
 * Initialize charts on current page
 */
function initializeChartsOnPage() {
    // This function will be extended by charts.js
    console.log('Initializing charts for module:', HRPlatform.currentModule);
}

/**
 * Setup form validations
 */
function setupFormValidations() {
    // Add Bootstrap validation classes
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Check for notifications
 */
function checkNotifications() {
    // This would typically check for server-side notifications
    // For now, we'll just log
    console.log('Checking for notifications...');
}

/**
 * Utility function to format numbers
 */
function formatNumber(num, decimals = 1) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(decimals) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(decimals) + 'K';
    }
    return num.toString();
}

/**
 * Utility function to format dates
 */
function formatDate(date, format = 'short') {
    const options = {
        short: { year: 'numeric', month: 'short', day: 'numeric' },
        long: { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' },
        time: { hour: '2-digit', minute: '2-digit' }
    };
    
    return new Intl.DateTimeFormat('en-US', options[format]).format(new Date(date));
}

/**
 * Utility function to debounce function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility function to throttle function calls
 */
function throttle(func, limit) {
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

/**
 * Smooth scroll to element
 */
function smoothScrollTo(elementId, offset = 0) {
    const element = document.getElementById(elementId);
    if (element) {
        const targetPosition = element.offsetTop - offset;
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard!', 'success', 2000);
    } catch (err) {
        showNotification('Failed to copy to clipboard', 'error');
    }
}

/**
 * Export data as CSV
 */
function exportToCSV(data, filename = 'hr-data.csv') {
    const csvContent = convertToCSV(data);
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

/**
 * Convert data to CSV format
 */
function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [
        headers.join(','),
        ...data.map(row => 
            headers.map(header => {
                const value = row[header];
                return typeof value === 'string' && value.includes(',') 
                    ? `"${value}"` 
                    : value;
            }).join(',')
        )
    ];
    
    return csvRows.join('\n');
}

/**
 * Print current page
 */
function printPage() {
    window.print();
}

/**
 * Toggle fullscreen mode
 */
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
}

// Export functions for use in other scripts
window.HRPlatform = HRPlatform;
window.showNotification = showNotification;
window.formatNumber = formatNumber;
window.formatDate = formatDate;
window.exportToCSV = exportToCSV;
window.copyToClipboard = copyToClipboard;
window.smoothScrollTo = smoothScrollTo;
