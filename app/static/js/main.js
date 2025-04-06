// This file contains additional JavaScript functions that can be used across the application

// Function to create a notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Fade in
    setTimeout(() => {
        notification.style.opacity = '1';
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 3000);
}

// Function to format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
}

// Function to calculate time difference and format as human-readable
function formatTimeDiff(startTime, endTime) {
    const diff = Math.floor((endTime - startTime) / 1000);
    
    if (diff < 60) {
        return `${diff} seconds`;
    } else if (diff < 3600) {
        const minutes = Math.floor(diff / 60);
        const seconds = diff % 60;
        return `${minutes} min ${seconds} sec`;
    } else {
        const hours = Math.floor(diff / 3600);
        const minutes = Math.floor((diff % 3600) / 60);
        return `${hours} hr ${minutes} min`;
    }
}

// Add event listener to all sliders to update their display values
document.addEventListener('DOMContentLoaded', function() {
    const sliders = document.querySelectorAll('input[type="range"]');
    
    sliders.forEach(slider => {
        const valueDisplay = document.getElementById(`${slider.id}Value`);
        if (valueDisplay) {
            // Set initial value
            valueDisplay.textContent = slider.value;
            
            // Update on change
            slider.addEventListener('input', function() {
                valueDisplay.textContent = this.value;
            });
        }
    });
});