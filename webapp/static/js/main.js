// Main JavaScript for Video to SOP Generator

// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'slideUp 0.3s ease-out';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });
});

// Add slideUp animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-10px);
        }
    }
`;
document.head.appendChild(style);

// Confirm before leaving page during form submission
let formSubmitting = false;

document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
        formSubmitting = true;
    });
});

window.addEventListener('beforeunload', function(e) {
    if (formSubmitting) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Table row click to view
document.querySelectorAll('.sops-table tbody tr').forEach(row => {
    const viewLink = row.querySelector('a[href*="/sop/"]');
    if (viewLink) {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking on action buttons
            if (!e.target.closest('.actions')) {
                window.location.href = viewLink.href;
            }
        });
    }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading indicator for buttons
document.querySelectorAll('button[type="submit"]').forEach(button => {
    const form = button.closest('form');
    if (form) {
        form.addEventListener('submit', function() {
            button.disabled = true;
            const originalText = button.textContent;
            button.textContent = '⏳ Processing...';
            
            // Re-enable after 30 seconds as failsafe
            setTimeout(() => {
                button.disabled = false;
                button.textContent = originalText;
            }, 30000);
        });
    }
});

// Format file sizes
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// Validate video file before upload
const videoInputs = document.querySelectorAll('input[type="file"][accept*="video"]');
videoInputs.forEach(input => {
    input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const maxSize = 500 * 1024 * 1024; // 500MB
            
            if (file.size > maxSize) {
                alert('File is too large! Maximum size is 500MB.');
                e.target.value = '';
                return;
            }
            
            const validTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/webm', 'video/x-matroska'];
            if (!validTypes.includes(file.type) && !file.name.match(/\.(mp4|avi|mov|webm|mkv)$/i)) {
                alert('Invalid file type! Please upload a video file (MP4, AVI, MOV, WebM, MKV).');
                e.target.value = '';
                return;
            }
        }
    });
});

// Add tooltips
const tooltipElements = document.querySelectorAll('[title]');
tooltipElements.forEach(element => {
    element.addEventListener('mouseenter', function() {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = this.getAttribute('title');
        tooltip.style.cssText = `
            position: absolute;
            background: #333;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            font-size: 0.875rem;
            z-index: 1000;
            pointer-events: none;
        `;
        document.body.appendChild(tooltip);
        
        const rect = this.getBoundingClientRect();
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
        tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
        
        this._tooltip = tooltip;
    });
    
    element.addEventListener('mouseleave', function() {
        if (this._tooltip) {
            this._tooltip.remove();
            delete this._tooltip;
        }
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K: Focus search (if exists)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[type="text"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape: Close modals or clear focus
    if (e.key === 'Escape') {
        document.activeElement.blur();
    }
});

// Add copy to clipboard functionality
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy:', err);
        });
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            showToast('Copied to clipboard!');
        } catch (err) {
            console.error('Failed to copy:', err);
        }
        document.body.removeChild(textarea);
    }
}

// Toast notification
function showToast(message, duration = 3000) {
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: #333;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, duration);
}

// Add slideIn/slideOut animations
const toastStyle = document.createElement('style');
toastStyle.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
`;
document.head.appendChild(toastStyle);

console.log('Video to SOP Generator - Web App loaded successfully!');
