document.addEventListener('DOMContentLoaded', function() {
    updateStatus();
    updateServices();
    animateStats();
    updateTime();
    initCardEffects();
    
    // Form submission
    const orderForm = document.getElementById('orderForm');
    if (orderForm) {
        orderForm.addEventListener('submit', handleOrderSubmit);
    }
});

async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        const statusElement = document.getElementById('status-message');
        if (statusElement) {
            statusElement.textContent = data.message;
        }
        
        // Update stats if needed
        if (data.stats && data.stats.projects_completed) {
            const projectsElement = document.querySelector('.stat-number:nth-child(1)');
            if (projectsElement) {
                projectsElement.textContent = data.stats.projects_completed;
            }
        }
        
    } catch (error) {
        console.log('Status update failed:', error);
    }
}

async function updateServices() {
    try {
        const response = await fetch('/api/services');
        const data = await response.json();
        console.log('Available services:', data.services);
    } catch (error) {
        console.log('Services update failed:', error);
    }
}

function animateStats() {
    const stats = document.querySelectorAll('.stat-number');
    stats.forEach(stat => {
        const text = stat.textContent;
        // Only animate if it's a number
        if (!isNaN(parseFloat(text))) {
            const target = parseFloat(text);
            let current = 0;
            const increment = target / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                // Format based on content
                if (text.includes('$')) {
                    stat.textContent = '$' + current.toFixed(2);
                } else {
                    stat.textContent = Math.round(current).toLocaleString();
                }
            }, 30);
        }
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

// Modal Functions
function showOrderModal(serviceType) {
    const modal = document.getElementById('orderModal');
    const serviceInput = document.getElementById('serviceType');
    const modalTitle = document.getElementById('modalTitle');
    
    // Set service type
    let serviceName = '';
    switch(serviceType) {
        case 'blender':
            serviceName = 'Blender Rendering ($0.04/frame)';
            break;
        case 'tensorflow':
            serviceName = 'TensorFlow GPU Compute ($0.10+/min)';
            break;
        case 'hashcracking':
            serviceName = 'Hash Cracking ($0.05/min)';
            break;
        default:
            serviceName = 'Compute Service';
    }
    
    serviceInput.value = serviceName;
    modalTitle.textContent = `Order ${serviceName.split(' ')[0]} Service`;
    modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('orderModal');
    modal.style.display = 'none';
    document.getElementById('orderForm').reset();
}

async function handleOrderSubmit(e) {
    e.preventDefault();
    
    const serviceType = document.getElementById('serviceType').value;
    const email = document.getElementById('email').value;
    const details = document.getElementById('details').value;
    const budget = document.getElementById('budget').value;
    
    // Simple validation
    if (!email || !details) {
        alert('Please fill in all required fields.');
        return;
    }
    
    // In a real app, you would send this to your server
    // For now, we'll just show a confirmation
    const modal = document.getElementById('orderModal');
    modal.style.display = 'none';
    
    // Show success message
    alert(`Thank you! Your ${serviceType.split(' ')[0]} job inquiry has been received.\n\nWe'll contact you at ${email} within 24 hours to discuss your project.\n\nDetails submitted: ${details.substring(0, 100)}...`);
    
    // Reset form
    document.getElementById('orderForm').reset();
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('orderModal');
    if (event.target === modal) {
        closeModal();
    }
}
