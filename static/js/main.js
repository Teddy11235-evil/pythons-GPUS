// Update dynamic content
document.addEventListener('DOMContentLoaded', function() {
    // Update live status
    updateStatus();
    
    // Update stats animation
    animateStats();
    
    // Update time dynamically
    updateTime();
    
    // Add hover effects
    initCardEffects();
});

async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update status badge
        const statusElement = document.getElementById('status-message');
        if (statusElement) {
            statusElement.textContent = data.message;
        }
        
        // Update services if needed
        updateServices(data.pricing_tiers);
        
    } catch (error) {
        console.log('Status update failed:', error);
    }
}

function updateServices(pricingTiers) {
    // This can be used to dynamically update pricing from API
    console.log('Available services:', pricingTiers);
}

function animateStats() {
    const stats = document.querySelectorAll('.stat-number');
    stats.forEach(stat => {
        const target = parseInt(stat.textContent);
        let current = 0;
        const increment = target / 50;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            stat.textContent = Math.round(current).toLocaleString();
        }, 30);
    });
}

function updateTime() {
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        setInterval(() => {
            const now = new Date();
            timeElement.textContent = now.toLocaleTimeString('en-US', {
                hour12: true,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }, 1000);
    }
}

function initCardEffects() {
    const cards = document.querySelectorAll('.service-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transition = 'all 0.3s ease';
        });
    });
}
