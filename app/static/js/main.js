/**
 * SupportSight - Main JavaScript
 */

// Sidebar Toggle & Responsive Navigation
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const desktopSidebarToggle = document.getElementById('desktopSidebarToggle');
    const mobileSidebarToggle = document.getElementById('mobileSidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    // Restore saved sidebar state for desktop
    if (window.innerWidth >= 992 && sidebar && mainContent) {
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isCollapsed) {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('sidebar-collapsed');
        }
    }

    function toggleDesktopSidebar() {
        if (!sidebar || !mainContent) return;
        const collapsed = sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('sidebar-collapsed');
        localStorage.setItem('sidebarCollapsed', collapsed);
    }

    function toggleMobileSidebar() {
        if (!sidebar || !sidebarOverlay) return;
        const isActive = sidebar.classList.toggle('active');
        sidebarOverlay.classList.toggle('active', isActive);
    }

    function closeMobileSidebar() {
        if (!sidebar || !sidebarOverlay) return;
        sidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
    }

    if (sidebarToggle) sidebarToggle.addEventListener('click', toggleDesktopSidebar);
    if (desktopSidebarToggle) desktopSidebarToggle.addEventListener('click', toggleDesktopSidebar);
    if (mobileSidebarToggle) mobileSidebarToggle.addEventListener('click', toggleMobileSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeMobileSidebar);

    // Close mobile drawer on Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && window.innerWidth < 992) {
            closeMobileSidebar();
        }
    });

    // Reset overlay on window resize to desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 992) {
            closeMobileSidebar();
        }
    });

    // Refresh button
    const refreshBtn = document.getElementById('refreshData');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            location.reload();
        });
    }

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Format bytes to human readable
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Format percentage
function formatPercent(value, decimals = 1) {
    if (value === null || value === undefined) return '0%';
    return value.toFixed(decimals) + '%';
}

// Format duration
function formatDuration(seconds) {
    if (!seconds) return '0s';

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    let result = '';
    if (hours > 0) result += hours + 'h ';
    if (minutes > 0) result += minutes + 'm ';
    if (secs > 0 || result === '') result += secs + 's';

    return result.trim();
}

// Debounce function
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

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(
        function() {
            showToast('Copied to clipboard!', 'success');
        },
        function() {
            showToast('Failed to copy', 'error');
        }
    );
}

// Toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class='bx bx-${type === 'success' ? 'check-circle' : type === 'error' ? 'x-circle' : 'info-circle'}'></i>
            <span>${message}</span>
        </div>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// API request helper
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const mergedOptions = { ...defaultOptions, ...options };

    try {
        const response = await fetch(url, mergedOptions);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Loading state
function setLoading(element, loading = true) {
    if (loading) {
        element.disabled = true;
        element.dataset.originalText = element.innerHTML;
        element.innerHTML = '<i class="bx bx-loader-alt bx-spin"></i> Loading...';
    } else {
        element.disabled = false;
        element.innerHTML = element.dataset.originalText || element.innerHTML;
    }
}

// Chart color helper
function getChartColors() {
    return {
        primary: '#0078D4',
        primaryLight: '#00bcf2',
        success: '#28a745',
        warning: '#ffc107',
        danger: '#dc3545',
        info: '#17a2b8',
        purple: '#8b5cf6',
        pink: '#ec4899',
    };
}

// Status color helper
function getStatusColor(value, thresholds = { critical: 90, warning: 70 }) {
    if (value >= thresholds.critical) return 'danger';
    if (value >= thresholds.warning) return 'warning';
    return 'success';
}

// Animate number
function animateNumber(element, start, end, duration, prefix = '', suffix = '') {
    const range = end - start;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = start + range * easeOutQuart;

        element.textContent = prefix + current.toFixed(0) + suffix;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// Export utilities
window.SupportSight = {
    formatBytes,
    formatPercent,
    formatDuration,
    debounce,
    copyToClipboard,
    showToast,
    apiRequest,
    setLoading,
    getChartColors,
    getStatusColor,
    animateNumber
};
