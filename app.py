from flask import Flask, render_template, jsonify, request, redirect, url_for
import requests
from datetime import datetime
import os
import random
import time
import json
from functools import lru_cache
import threading

app = Flask(__name__)

# ===== CONFIGURATION =====
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1445098227815944192/9RuBPnQoe6wYDmtqnDHpf7PB401_lS9BfNKkCeYT4DhQyRCc4HUaRep8tiPqE594rLpI"
ABOUT_FILE_URL = "https://raw.githubusercontent.com/Teddy11235-evil/pythons-GPUS/main/about.txt"
PRICES_FILE_URL = "https://raw.githubusercontent.com/Teddy11235-evil/pythons-GPUS/main/prices.txt"

# Cache Manager
class CacheManager:
    def __init__(self, ttl=300):
        self.ttl = ttl
        self.cache = {}
        self.lock = threading.Lock()
    
    def get(self, key):
        with self.lock:
            if key in self.cache:
                data, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    return data
            return None
    
    def set(self, key, value):
        with self.lock:
            self.cache[key] = (value, time.time())
    
    def clear(self, key=None):
        with self.lock:
            if key:
                self.cache.pop(key, None)
            else:
                self.cache.clear()

cache = CacheManager(ttl=300)

# ===== DISCORD WEBHOOK FUNCTIONS =====
def send_discord_async(content, username="Python's GPUS Bot"):
    """Send message to Discord in background thread"""
    def send():
        try:
            payload = {
                "content": content,
                "username": username,
                "avatar_url": "https://cdn-icons-png.flaticon.com/512/3094/3094067.png"
            }
            response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
            print(f"[Discord] Response: {response.status_code}")
        except Exception as e:
            print(f"[Discord] Async send error: {e}")
    
    thread = threading.Thread(target=send)
    thread.daemon = True
    thread.start()
    return thread

def format_order_message(order_data):
    """Format order data for Discord with proper boolean handling"""
    # Debug the incoming data
    print(f"[Format Debug] Order data received: {json.dumps(order_data, indent=2)}")
    
    # Get boolean values - handle different formats
    bargain = order_data.get('bargain', False)
    priority = order_data.get('priority', False)
    
    print(f"[Format Debug] Raw bargain: {bargain}, type: {type(bargain)}")
    print(f"[Format Debug] Raw priority: {priority}, type: {type(priority)}")
    
    # Convert to boolean
    def to_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', 'on', 'yes', '1']
        if isinstance(value, (int, float)):
            return bool(value)
        return False
    
    bargain_bool = to_bool(bargain)
    priority_bool = to_bool(priority)
    
    print(f"[Format Debug] Processed bargain: {bargain_bool}")
    print(f"[Format Debug] Processed priority: {priority_bool}")
    
    # Get and truncate notes
    notes = order_data.get('notes', 'No additional notes')
    if len(notes) > 400:
        notes = notes[:397] + "..."
    
    # Get user agent and truncate
    user_agent = order_data.get('user_agent', 'Unknown')
    if len(user_agent) > 100:
        user_agent = user_agent[:97] + "..."
    
    # Format the message
    return f"""```yaml
📦 NEW ORDER RECEIVED
════════════════════════════════════════
📧 Contact Email: {order_data.get('email', 'Not provided')}
⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🆔 Order ID: {order_data.get('id', f"TEMP-{int(time.time())}")}

🛒 ORDER DETAILS:
────────────────────────────────────────
• Service Type: {order_data.get('service_type', 'Blender Rendering')}
• Project Link: {order_data.get('project_link', 'Not provided')}
• Estimated Frames: {order_data.get('frame_count', 'Not specified')}
• Bargain Requested: {'✅ YES' if bargain_bool else '❌ NO'}
• High Priority: {'✅ YES (1.5x price)' if priority_bool else '❌ NO'}
• Base Price/Frame: {order_data.get('base_price', '$0.04')}
• Priority Multiplier: {order_data.get('multiplier', '1x')}
• Estimated Total: {order_data.get('estimated_total', 'Not calculated')}

📝 ADDITIONAL NOTES ({len(notes)} chars):
────────────────────────────────────────
{notes}

🌐 CLIENT INFORMATION:
────────────────────────────────────────
• IP Address: {order_data.get('user_ip', 'Not recorded')}
• User Agent: {user_agent}
• Referrer: {order_data.get('referrer', 'Direct visit')}

⚠️ SERVICE STATUS: UNDER DEVELOPMENT
════════════════════════════════════════
This is a pre-order request. Service is currently in development.
The customer will be contacted when the service becomes available.
```"""

def notify_new_order(order_data):
    """Send order notification to Discord"""
    message = format_order_message(order_data)
    print(f"[Notify] Sending to Discord: {order_data.get('email')}")
    print(f"[Notify] Bargain: {order_data.get('bargain')}")
    print(f"[Notify] Priority: {order_data.get('priority')}")
    send_discord_async(message, "🎉 New Order")
    return True

# ===== GITHUB FETCHING =====
@lru_cache(maxsize=2)
def fetch_github_content(url):
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        return response.text
    except:
        return None

def get_prices():
    cached = cache.get('prices')
    if cached:
        return cached
    
    content = fetch_github_content(PRICES_FILE_URL)
    prices = {
        'blender_per_frame': '$0.04',
        'hash_per_minute': '$0.05',
        'tensorflow_base': '$0.10',
        'priority_multiplier': '1.5x',
        'status': 'development'
    }
    
    if content:
        for line in content.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                prices[key.strip().lower()] = value.strip()
    
    cache.set('prices', prices)
    return prices

def get_about_content():
    cached = cache.get('about')
    if cached:
        return cached
    
    content = fetch_github_content(ABOUT_FILE_URL)
    if not content:
        content = "# About Our Compute Service\n\nContent loading..."
    
    cache.set('about', content)
    return content

# ===== ROUTES =====
@app.route('/')
def home():
    prices = get_prices()
    return render_template('index.html', 
                         prices=prices, 
                         user_count=random.randint(1, 15))

@app.route('/toggle-dark-mode', methods=['POST'])
def toggle_dark_mode():
    data = request.get_json()
    dark_mode = data.get('dark_mode', False)
    return jsonify({'success': True, 'dark_mode': dark_mode})

@app.route('/about')
def about():
    content = get_about_content()
    return render_template('about.html', content=content)

@app.route('/blender-order', methods=['GET', 'POST'])
def blender_order():
    if request.method == 'GET':
        prices = get_prices()
        return render_template('blender_order.html', prices=prices)
    
    # POST request - process order
    try:
        # Get form data - IMPORTANT: checkboxes only appear in form when checked!
        email = request.form.get('email', '').strip()
        project_link = request.form.get('project_link', '').strip()
        
        # Checkboxes: if present in form, they are checked. If not present, they are unchecked.
        bargain = 'bargain' in request.form
        priority = 'priority' in request.form
        
        notes = request.form.get('notes', '').strip()
        frame_count = request.form.get('frame_count', '100')
        
        # Debug output
        print(f"\n=== FORM DATA RECEIVED ===")
        print(f"All form keys: {list(request.form.keys())}")
        print(f"Email: {email}")
        print(f"Bargain key in form: {'bargain' in request.form}")
        print(f"Priority key in form: {'priority' in request.form}")
        print(f"Notes length: {len(notes)}")
        print(f"Frame count: {frame_count}")
        print("=========================\n")
        
        # Calculate price
        prices = get_prices()
        base_price = float(prices['blender_per_frame'].replace('$', ''))
        multiplier = 1.5 if priority else 1.0
        estimated_total = f"${base_price * int(frame_count) * multiplier:.2f}"
        
        # Truncate notes to 400 characters for Discord
        discord_notes = notes[:400] if len(notes) > 400 else notes
        
        # Prepare order data
        order_data = {
            'email': email,
            'project_link': project_link,
            'bargain': bargain,  # This is now a proper boolean
            'priority': priority,  # This is now a proper boolean
            'notes': discord_notes,
            'original_notes': notes,
            'frame_count': frame_count,
            'service_type': 'Blender Rendering',
            'base_price': prices['blender_per_frame'],
            'multiplier': f"{multiplier}x",
            'estimated_total': estimated_total,
            'user_ip': request.headers.get('X-Forwarded-For', request.remote_addr),
            'user_agent': request.headers.get('User-Agent', 'Unknown')[:100],
            'referrer': request.headers.get('Referer', 'Direct'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to Discord (async)
        notify_new_order(order_data)
        
        # Save locally (non-blocking) with full notes
        order_data['notes'] = notes  # Restore full notes for local storage
        thread = threading.Thread(target=save_order_locally, args=(order_data,))
        thread.daemon = True
        thread.start()
        
        # Redirect to confirmation
        return redirect(url_for('order_confirmation', service='blender'))
        
    except Exception as e:
        print(f"Order processing error: {e}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('blender_order'))

def save_order_locally(order_data):
    """Save order to JSON file (background task)"""
    try:
        orders_file = 'orders.json'
        orders = []
        
        if os.path.exists(orders_file):
            try:
                with open(orders_file, 'r') as f:
                    orders = json.load(f)
            except:
                orders = []
        
        order_data['id'] = f"ORD-{int(time.time())}"
        orders.append(order_data)
        
        # Keep only last 100 orders
        if len(orders) > 100:
            orders = orders[-100:]
        
        with open(orders_file, 'w') as f:
            json.dump(orders, f, indent=2, default=str)
            
        print(f"[Order Saved] ID: {order_data['id']}, Email: {order_data['email']}")
        print(f"[Order Saved] Bargain: {order_data.get('bargain')}")
        print(f"[Order Saved] Priority: {order_data.get('priority')}")
        
    except Exception as e:
        print(f"[Save Error] Failed to save order: {e}")

@app.route('/order-confirmation/<service>')
def order_confirmation(service):
    return render_template('order_confirmation.html', service=service)

@app.route('/api/order', methods=['POST'])
def api_order():
    """API endpoint for external order submissions"""
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Process boolean values
        bargain = data.get('bargain', False)
        priority = data.get('priority', False)
        
        # Convert string values to boolean
        if isinstance(bargain, str):
            bargain = bargain.lower() in ['true', 'on', 'yes', '1']
        if isinstance(priority, str):
            priority = priority.lower() in ['true', 'on', 'yes', '1']
        
        # Truncate notes
        notes = data.get('notes', '')
        if len(notes) > 400:
            notes = notes[:397] + "..."
        
        # Add metadata
        data.update({
            'user_ip': request.headers.get('X-Forwarded-For', request.remote_addr),
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'timestamp': datetime.now().isoformat(),
            'source': 'api',
            'bargain': bargain,
            'priority': priority,
            'notes': notes
        })
        
        # Send to Discord
        notify_new_order(data)
        
        # Save locally
        save_order_locally(data)
        
        return jsonify({
            'success': True,
            'message': 'Order received',
            'order_id': f"API-{int(time.time())}"
        })
        
    except Exception as e:
        print(f"[API Error] {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/prices')
def api_prices():
    prices = get_prices()
    return jsonify(prices)

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'service': 'pythons-gpus-store',
        'version': '1.6.0',
        'discord_webhook': 'active'
    })

@app.route('/webhook/test')
def test_webhook():
    """Test Discord webhook with sample data"""
    test_data = {
        'email': 'test@example.com',
        'project_link': 'https://example.com/test.blend',
        'bargain': True,
        'priority': True,
        'notes': 'This is a test order with bargain and priority enabled. ' * 10,
        'frame_count': '50',
        'service_type': 'Blender Rendering',
        'base_price': '$0.04',
        'multiplier': '1.5x',
        'estimated_total': '$3.00',
        'user_ip': '192.168.1.100',
        'user_agent': 'Mozilla/5.0 Test Browser',
        'referrer': 'Test Page'
    }
    
    message = format_order_message(test_data)
    send_discord_async(message, "🔄 Test Order")
    
    return jsonify({
        'success': True,
        'message': 'Test order sent to Discord',
        'test_data': test_data
    })

@app.route('/webhook/debug')
def debug_webhook():
    """Debug endpoint to check webhook configuration"""
    return jsonify({
        'webhook_url': DISCORD_WEBHOOK_URL[:50] + '...' if DISCORD_WEBHOOK_URL else 'Not set',
        'status': 'Configured' if DISCORD_WEBHOOK_URL else 'Not configured',
        'test_endpoint': '/webhook/test'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/orders/debug', methods=['GET'])
def debug_orders():
    """Debug endpoint to see recent orders"""
    try:
        if os.path.exists('orders.json'):
            with open('orders.json', 'r') as f:
                orders = json.load(f)
            recent = orders[-5:] if len(orders) > 5 else orders
            return jsonify({
                'total_orders': len(orders),
                'recent_orders': recent
            })
        else:
            return jsonify({'total_orders': 0, 'recent_orders': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    error_msg = f"""```yaml
🚨 SERVER ERROR
• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• Error: {str(e)}
• Path: {request.path}
```"""
    send_discord_async(error_msg, "🚨 Error Alert")
    return render_template('500.html', error=str(e)), 500

# ===== STARTUP =====
# Flag to track if startup has run
_startup_has_run = False

@app.before_request
def startup_tasks():
    """Run once on startup"""
    global _startup_has_run
    if not _startup_has_run:
        startup_msg = f"""```yaml
🚀 SERVER STARTED
════════════════════════════════════════
• Service: Python's GPUS Store v1.6.0
• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• Environment: {'Production' if os.environ.get('RENDER') else 'Development'}
• Discord Webhook: {'✅ Active' if DISCORD_WEBHOOK_URL else '❌ Inactive'}
════════════════════════════════════════
```"""
        send_discord_async(startup_msg, "🚀 Server Startup")
        print("[Startup] Server initialized with Discord webhook support")
        _startup_has_run = True

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
