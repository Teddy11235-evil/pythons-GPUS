// static/js/main.js - Complete JavaScript for Python's GPUS

// ===== GLOBAL VARIABLES =====
let currentTheme = localStorage.getItem('theme') || 'light';

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('Python\'s GPUS - Initializing...');
    
    // Initialize theme
    initTheme();
    
    // Initialize time display
    initTimeDisplay();
    
    // Initialize rock meme info
    initRockInfo();
    
    // Initialize service card effects
    initServiceCards();
    
    // Initialize stats animation
    initStatsAnimation();
    
    // Initialize form handling if on order page
    if (document.getElementById('order-form')) {
        initOrderForm();
    }
    
    // Initialize API status updates
    initStatusUpdates();
    
    console.log('Initialization complete.');
});

// ===== THEME MANAGEMENT =====
function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    
    // Set initial theme
    if (currentTheme === 'dark') {
        html.setAttribute('data-theme', 'dark');
        if (themeToggle) themeToggle.checked = true;
    } else {
        html.setAttribute('data-theme', 'light');
        if (themeToggle) themeToggle.checked = false;
    }
    
    // Add toggle event listener
    if (themeToggle) {
        themeToggle.addEventListener('change', function() {
            currentTheme = this.checked ? 'dark' : 'light';
            html.setAttribute('data-theme', currentTheme);
            localStorage.setItem('theme', currentTheme);
            
            // Notify server (optional)
            fetch('/toggle-dark-mode', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({dark_mode: this.checked})
            }).catch(console.error);
        });
    }
}

// ===== TIME DISPLAY =====
function initTimeDisplay() {
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        updateTime();
        setInterval(updateTime, 1000);
    }
}

function updateTime() {
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        const now = new Date();
        timeElement.textContent = now.toLocaleTimeString('en-US', {
            hour12: true,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
}

// ===== ROCK MEME INFO =====
function initRockInfo() {
    updateRockInfo();
    setInterval(updateRockInfo, 10000);
}

async function updateRockInfo() {
    try {
        // Get IP (simulated for demo)
        const ipElement = document.getElementById('user-ip');
        if (ipElement && ipElement.textContent === 'Loading...') {
            ipElement.textContent = generateRandomIP();
        }
        
        // Get server status
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update elements
        updateElement('server-ping', data.server_ping + 'ms');
        updateElement('online-users', data.user_count);
        updateElement('online-count', data.user_count);
        
        // Update server status indicator
        const statusElement = document.getElementById('server-status');
        if (statusElement) {
            statusElement.innerHTML = '🟢 Online';
            statusElement.title = `Version: ${data.version}`;
        }
        
    } catch (error) {
        console.log('Failed to update rock info:', error);
        updateElement('server-ping', '--');
        updateElement('online-users', '--');
        updateElement('online-count', '--');
        
        const statusElement = document.getElementById('server-status');
        if (statusElement) {
            statusElement.innerHTML = '🟡 Connecting...';
        }
    }
}

function generateRandomIP() {
    return `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;
}

function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        // Add animation for number changes
        if (!isNaN(parseFloat(element.textContent)) && !isNaN(parseFloat(value))) {
            element.classList.add('updating');
            setTimeout(() => {
                element.textContent = value;
                element.classList.remove('updating');
            }, 100);
        } else {
            element.textContent = value;
        }
    }
}

// ===== SERVICE CARDS =====
function initServiceCards() {
    const serviceCards = document.querySelectorAll('.service-card');
    
    serviceCards.forEach(card => {
        // Add hover effects
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 25px var(--shadow-hover)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 20px var(--shadow-color)';
        });
        
        // Add click handler for unavailable services
        const button = card.querySelector('.cta-button');
        if (button && button.disabled) {
            card.addEventListener('click', function() {
                showComingSoonModal(this.querySelector('h3').textContent);
            });
        }
    });
}

// ===== STATS ANIMATION =====
function initStatsAnimation() {
    const stats = document.querySelectorAll('.stat-number');
    
    stats.forEach(stat => {
        const text = stat.textContent;
        
        // Only animate if it's a number (not currency or percentage)
        if (!isNaN(parseFloat(text.replace('$', '').replace('%', '').replace('+', '')))) {
            const target = parseFloat(text.replace('$', '').replace('%', '').replace('+', ''));
            let current = 0;
            const increment = target / 50;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                
                // Format based on original content
                if (text.includes('$')) {
                    stat.textContent = '$' + current.toFixed(2);
                } else if (text.includes('%')) {
                    stat.textContent = current.toFixed(1) + '%';
                } else if (text.includes('+')) {
                    stat.textContent = Math.round(current) + '+';
                } else {
                    stat.textContent = Math.round(current);
                }
            }, 30);
        }
    });
}

// ===== ORDER FORM HANDLING =====
function initOrderForm() {
    console.log('Initializing order form...');
    
    // Set up notes counter
    const notesTextarea = document.getElementById('notes');
    if (notesTextarea) {
        notesTextarea.addEventListener('input', updateNotesCounter);
        updateNotesCounter.call(notesTextarea);
    }
    
    // Load draft if exists
    loadFormDraft();
    
    // Set up auto-save
    setupAutoSave();
    
    // Initialize price summary
    if (typeof updatePriceSummary === 'function') {
        updatePriceSummary();
    }
}

function updateNotesCounter() {
    const counter = document.getElementById('notes-count');
    if (counter) {
        const length = this.value.length;
        counter.textContent = length;
        
        // Color coding
        if (length > 350) {
            counter.style.color = 'var(--warning)';
            counter.style.fontWeight = 'bold';
        } else if (length > 300) {
            counter.style.color = 'var(--warning)';
        } else {
            counter.style.color = 'var(--text-secondary)';
            counter.style.fontWeight = 'normal';
        }
    }
}

function loadFormDraft() {
    try {
        const saved = localStorage.getItem('blenderOrderDraft');
        if (saved) {
            const data = JSON.parse(saved);
            
            // Restore values
            if (data.email) document.getElementById('email').value = data.email;
            if (data.frame_count) document.getElementById('frame_count').value = data.frame_count;
            if (data.project_link) document.getElementById('project_link').value = data.project_link;
            if (data.priority !== undefined) document.getElementById('priority').checked = data.priority;
            if (data.bargain !== undefined) document.getElementById('bargain').checked = data.bargain;
            if (data.notes) document.getElementById('notes').value = data.notes;
            
            console.log('Form draft loaded');
        }
    } catch (error) {
        console.error('Error loading draft:', error);
        localStorage.removeItem('blenderOrderDraft');
    }
}

function saveFormDraft() {
    try {
        const draft = {
            email: document.getElementById('email').value,
            frame_count: document.getElementById('frame_count').value,
            project_link: document.getElementById('project_link').value,
            priority: document.getElementById('priority').checked,
            bargain: document.getElementById('bargain').checked,
            notes: document.getElementById('notes').value,
            timestamp: new Date().toISOString()
        };
        
        localStorage.setItem('blenderOrderDraft', JSON.stringify(draft));
    } catch (error) {
        console.error('Error saving draft:', error);
    }
}

function setupAutoSave() {
    const form = document.getElementById('order-form');
    if (!form) return;
    
    // Save on input
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('input', saveFormDraft);
        input.addEventListener('change', saveFormDraft);
    });
    
    // Auto-save every 30 seconds
    setInterval(saveFormDraft, 30000);
    
    // Clear draft on successful submission
    form.addEventListener('submit', function() {
        setTimeout(() => {
            localStorage.removeItem('blenderOrderDraft');
        }, 1000);
    });
}

// ===== MODAL FUNCTIONS =====
function showComingSoonModal(serviceName) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal">
            <div class="modal-header">
                <h3><i class="fas fa-tools"></i> Coming Soon</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
            </div>
            <div class="modal-content">
                <div class="coming-soon-icon">
                    <i class="fas fa-cogs fa-3x"></i>
                </div>
                <h4>${serviceName} Service</h4>
                <p>This service is currently under development and will be available soon.</p>
                <p>We're working hard to bring you the best GPU compute experience!</p>
                <div class="progress-indicator">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 65%"></div>
                    </div>
                    <p class="progress-text">Development in progress...</p>
                </div>
                <button class="btn btn-primary" onclick="this.closest('.modal-overlay').remove()">
                    Got It!
                </button>
            </div>
        </div>
    `;
    
    // Add styles if not already present
    if (!document.getElementById('modal-styles')) {
        const style = document.createElement('style');
        style.id = 'modal-styles';
        style.textContent = `
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
            }
            .modal {
                background: var(--card-bg);
                border-radius: 12px;
                width: 90%;
                max-width: 500px;
                border: 1px solid var(--border-color);
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            }
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 1.5rem;
                border-bottom: 1px solid var(--border-color);
            }
            .modal-close {
                background: none;
                border: none;
                font-size: 1.5rem;
                cursor: pointer;
                color: var(--text-secondary);
            }
            .modal-content {
                padding: 2rem;
                text-align: center;
            }
            .coming-soon-icon {
                margin-bottom: 1.5rem;
                color: var(--accent-primary);
            }
            .progress-indicator {
                margin: 2rem 0;
            }
            .progress-bar {
                height: 8px;
                background: var(--bg-tertiary);
                border-radius: 4px;
                overflow: hidden;
                margin-bottom: 0.5rem;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
                border-radius: 4px;
                animation: progress-pulse 2s ease-in-out infinite;
            }
            @keyframes progress-pulse {
                0%, 100% { width: 65%; }
                50% { width: 70%; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(modal);
}

// ===== API STATUS UPDATES =====
function initStatusUpdates() {
    // Update prices every 2 minutes
    setInterval(updatePricesFromAPI, 120000);
    
    // Initial update
    updatePricesFromAPI();
}

async function updatePricesFromAPI() {
    try {
        const response = await fetch('/api/prices');
        const prices = await response.json();
        
        // Update price displays on homepage
        const priceElements = {
            'blender-price': prices.blender_per_frame,
            'hash-price': prices.hash_per_minute,
            'dynamic-blender-price': `${prices.blender_per_frame} per frame`,
            'dynamic-hash-price': `${prices.hash_per_minute} per minute`,
            'dynamic-tf-price': `From ${prices.tensorflow_base}/min`,
            'priority-multiplier': prices.priority_multiplier
        };
        
        for (const [id, value] of Object.entries(priceElements)) {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                element.classList.add('price-update');
                setTimeout(() => element.classList.remove('price-update'), 300);
            }
        }
        
    } catch (error) {
        console.log('Price update failed:', error);
    }
}

// ===== UTILITY FUNCTIONS =====
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles if not present
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--card-bg);
                border-left: 4px solid;
                border-radius: 8px;
                padding: 1rem 1.5rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 9999;
                transform: translateX(100%);
                opacity: 0;
                animation: slideIn 0.3s ease forwards;
            }
            .notification-success { border-color: var(--success); }
            .notification-info { border-color: var(--info); }
            .notification-warning { border-color: var(--warning); }
            .notification-error { border-color: var(--danger); }
            .notification-content {
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }
            .notification-content i { font-size: 1.2rem; }
            .notification-success i { color: var(--success); }
            .notification-info i { color: var(--info); }
            .notification-warning i { color: var(--warning); }
            .notification-error i { color: var(--danger); }
            @keyframes slideIn {
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'info': 'info-circle',
        'warning': 'exclamation-triangle',
        'error': 'exclamation-circle'
    };
    return icons[type] || 'info-circle';
}

// ===== EXPORT FOR DEBUGGING =====
window.pythonsGPUS = {
    version: '1.0.0',
    debug: {
        getTheme: () => currentTheme,
        getFormDraft: () => JSON.parse(localStorage.getItem('blenderOrderDraft') || '{}'),
        clearDraft: () => localStorage.removeItem('blenderOrderDraft'),
        testNotification: (type = 'info') => showNotification(`Test ${type} notification`, type),
        updateRockInfo: () => updateRockInfo()
    }
};

console.log('Python\'s GPUS JavaScript loaded successfully.');
console.log('Debug tools available at: window.pythonsGPUS.debug');
