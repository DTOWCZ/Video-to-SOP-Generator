// Main JavaScript for SOP Generator

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-info)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Password confirmation check
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    
    if (password && confirmPassword) {
        confirmPassword.addEventListener('input', function() {
            if (password.value !== confirmPassword.value) {
                confirmPassword.setCustomValidity('Passwords do not match');
            } else {
                confirmPassword.setCustomValidity('');
            }
        });
    }

    // File size validation
    const videoInput = document.getElementById('video');
    if (videoInput) {
        videoInput.addEventListener('change', function() {
            const maxSize = 500 * 1024 * 1024; // 500MB
            if (this.files[0] && this.files[0].size > maxSize) {
                alert('File size exceeds 500MB limit. Please choose a smaller file.');
                this.value = '';
            }
        });
    }

    console.log('SOP Generator initialized');
});
