document.addEventListener('DOMContentLoaded', function() {
    updateStatus();
    updateServices();
    animateStats();
    updateTime();
    initCardEffects();
    updateRockInfo();
    
    // Form submission
    const orderForm = document.getElementById('orderForm');
    if (orderForm) {
        orderForm.addEventListener('submit', handleOrderSubmit);
    }
    
    // Auto-update prices every 30 seconds
    setInterval(updatePrices, 30000);
});

async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        const statusElement = document.getElementById('status-message');
        if (statusElement) {
            if (data.status === 'development') {
                statusElement.innerHTML = 'Services under development - Coming soon! <i class="fas fa-tools"></i>';
                statusElement.style.color = '#f59e0b';
            } else {
                statusElement.textContent = data.message;
            }
        }
        
        // Update stats
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

async function updatePrices() {
    try {
        const response = await fetch('/api/prices');
        const prices = await response.json();
        
        // Update price displays
        const elements = {
            'blender-price': prices.blender_per_frame,
            'hash-price': prices.hash_per_minute,
            'priority-multiplier': prices.priority_multiplier,
            'dynamic-blender-price': `${prices.blender_per_frame} per frame`,
            'dynamic-tf-price': `From ${prices.tensorflow_base}/min`,
            'dynamic-hash-price': `${prices.hash_per_minute} per minute`
        };
        
        for (const [id, value] of Object.entries(elements)) {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        }
        
        console.log('Prices updated from GitHub');
        
    } catch (error) {
        console.log('Price update failed:', error);
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

async function updateRockInfo() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update IP (simulated since we can't get real IP from client-side JS easily)
        const ipElement = document.getElementById('user-ip');
        if (ipElement) {
            // Generate a fake IP for demo purposes
            const fakeIP = `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;
            ipElement.textContent = fakeIP;
        }
        
        // Update ping
        const pingElement = document.getElementById('server-ping');
        if (pingElement && data.server_ping) {
            pingElement.textContent = data.server_ping;
        }
        
        // Update user count
        const userElement = document.getElementById('online-users');
        if (userElement && data.user_count) {
            userElement.textContent = data.user_count;
            
            // Add some animation when user count changes
            userElement.style.transform = 'scale(1.2)';
            setTimeout(() => {
                userElement.style.transform = 'scale(1)';
            }, 300);
        }
        
    } catch (error) {
        console.log('Rock info update failed:', error);
    }
    
    // Update rock info every 10 seconds
    setTimeout(updateRockInfo, 10000);
}

function animateStats() {
    const stats = document.querySelectorAll('.stat-number');
    stats.forEach(stat => {
        const text = stat.textContent;
        if (!isNaN(parseFloat(text.replace('$', '').replace('x', '')))) {
            const target = parseFloat(text.replace('$', '').replace('x', ''));
            let current = 0;
            const increment = target / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                if (text.includes('$')) {
                    stat.textContent = '$' + current.toFixed(2);
                } else if (text.includes('x')) {
                    stat.textContent = current.toFixed(1) + 'x';
                } else {
                    stat.textContent = Math.round(current);
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

function showComingSoon(serviceType) {
    const modal = document.getElementById('comingSoonModal');
    const serviceName = document.getElementById('modal-service-name');
    
    let serviceText = '';
    switch(serviceType) {
        case 'tensorflow':
            serviceText = 'TensorFlow GPU Compute service is currently under development.';
            break;
        case 'hashcracking':
            serviceText = 'Hash Cracking service is currently under development.';
            break;
        default:
            serviceText = 'This service is currently under development.';
    }
    
    serviceName.textContent = serviceText;
    modal.style.display = 'flex';
    
    // Animate progress bar
    const progressFill = document.getElementById('progress-fill');
    let width = 60;
    const progressInterval = setInterval(() => {
        width = width === 60 ? 65 : 60;
        progressFill.style.width = width + '%';
    }, 2000);
    
    // Store interval to clear later
    modal.dataset.interval = progressInterval;
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'none';
    
    // Clear progress interval if exists
    if (modal.dataset.interval) {
        clearInterval(parseInt(modal.dataset.interval));
    }
}

async function handleOrderSubmit(e) {
    e.preventDefault();
    
    const serviceType = document.getElementById('serviceType')?.value || 'blender';
    const email = document.getElementById('email').value;
    const details = document.getElementById('details')?.value || '';
    
    // Simple validation
    if (!email) {
        alert('Please fill in all required fields.');
        return;
    }
    
    // In production, you would send this to your server
    console.log('Order submitted:', { email, serviceType, details });
    
    // Show success message
    alert(`Thank you! Your order request has been received.\n\nWe'll contact you at ${email} within 24 hours.\n\nNote: This service is under development - we'll notify you when it's ready.`);
    
    // Reset form if exists
    if (document.getElementById('orderForm')) {
        document.getElementById('orderForm').reset();
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modals = ['comingSoonModal', 'orderModal'];
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (event.target === modal) {
            closeModal(modalId);
        }
    });
}

// Initialize price update on load
updatePrices();
