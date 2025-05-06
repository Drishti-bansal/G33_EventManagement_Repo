// Custom JavaScript for Event Management app

// Enable tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add animation to alerts for auto-dismissal
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // Close after 5 seconds
    });
    
    // Date time picker enhancement
    const dateFields = document.querySelectorAll('input[type="datetime-local"]');
    dateFields.forEach(field => {
        if (!field.value) {
            // Set default to current time + 1 hour, rounded to nearest hour
            const now = new Date();
            now.setHours(now.getHours() + 1);
            now.setMinutes(0);
            now.setSeconds(0);
            
            // Format date for datetime-local input
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            
            field.value = `${year}-${month}-${day}T${hours}:${minutes}`;
        }
    });
});