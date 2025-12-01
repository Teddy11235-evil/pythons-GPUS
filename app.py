from flask import Flask, render_template, jsonify, request, redirect, url_for
import requests
from datetime import datetime
import os
import random
import time
import json

app = Flask(__name__)

# Discord Webhook URL (your provided URL)
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1445098227815944192/9RuBPnQoe6wYDmtqnDHpf7PB401_lS9BfNKkCeYT4DhQyRCc4HUaRep8tiPqE594rLpI"

# GitHub URLs
ABOUT_FILE_URL = "https://raw.githubusercontent.com/Teddy11235-evil/pythons-GPUS/main/about.txt"
PRICES_FILE_URL = "https://raw.githubusercontent.com/Teddy11235-evil/pythons-GPUS/main/prices.txt"

# Cache
cache = {'prices': {}, 'about': '', 'last_fetch': 0}
CACHE_TIMEOUT = 300

# ===== DISCORD WEBHOOK FUNCTIONS =====
def send_discord_order_notification(order_data):
    """Send formatted order information to Discord"""
    if not DISCORD_WEBHOOK_URL:
        print("[Discord] Webhook URL not configured")
        return False
    
    # Create formatted message in code block
    formatted_message = f"""```yaml
📦 NEW ORDER RECEIVED
════════════════════════════════════════
📧 Contact Email: {order_data.get('email', 'Not provided')}
⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🛒 Order Details:
────────────────────────────────────────
• Service Type: {order_data.get('service_type', 'Not specified')}
• Project Link: {order_data.get('project_link', 'Not provided')}
• Estimated Frames: {order_data.get('frame_count', 'Not specified')}
• Bargain Requested: {'✅ Yes' if order_data.get('bargain') else '❌ No'}
• High Priority: {'✅ Yes (1.5x price)' if order_data.get('priority') else '❌ No'}
• Notes: {order_data.get('notes', 'No additional notes')}

💰 Price Estimate:
────────────────────────────────────────
• Base Price/Frame: {order_data.get('base_price', '$0.04')}
• Priority Multiplier: {order_data.get('multiplier', '1x')}
• Estimated Total: {order_data.get('estimated_total', 'Not calculated')}

🌐 Website Info:
────────────────────────────────────────
• IP Address: {order_data.get('user_ip', 'Not recorded')}
• User Agent: {order_data.get('user_agent', 'Not recorded')}
• Referrer: {order_data.get('referrer', 'Direct visit')}

⚠️ Status: UNDER DEVELOPMENT
════════════════════════════════════════
This is a pre-order request. Service is in development.
```"""
    
    # Create embed with code block
    embed = {
        "title": "🎉 New Blender Render Order!",
        "description": "A new order has been submitted to the website.",
        "color": 0x00ff00,  # Green
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": "Python's GPUS Order System",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/5968/5968350.png"
        },
        "fields": [
            {
                "name": "Quick Info",
                "value": f"**Email:** {order_data.get('email', 'N/A')}\n**Service:** {order_data.get('service_type', 'N/A')}\n**Frames:** {order_data.get('frame_count', 'N/A')}",
                "inline": True
            },
            {
                "name": "Options",
                "value": f"**Bargain:** {'Yes' if order_data.get('bargain') else 'No'}\n**Priority:** {'Yes' if order_data.get('priority') else 'No'}\n**Status:** Under Development",
                "inline": True
            }
        ]
    }
    
    # Create payload with both code block and embed
    payload = {
        "content": formatted_message,
        "username": "Python's GPUS Order Bot",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/3094/3094067.png",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code in [200, 204]:
            print(f"[Discord] Order notification sent successfully")
            return True
        else:
            print(f"[Discord] Failed to send: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[Discord] Error sending notification: {e}")
        return False

def send_discord_test():
    """Send a test message to Discord"""
    test_message = """```yaml
✅ WEBHOOK TEST SUCCESSFUL
════════════════════════════════════════
• Service: Python's GPUS Server
• Status: ✅ Operational
• Time: {time}
• Test: Discord Webhook Integration
════════════════════════════════════════
This confirms your Discord webhook is working correctly!
```""".format(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    payload = {
        "content": test_message,
        "username": "Python's GPUS Test Bot",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/190/190411.png"
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        return response.status_code in [200, 204]
    except:
        return False

# ===== HELPER FUNCTIONS =====
def fetch_from_github(url):
    """Fetch content from GitHub"""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching from GitHub {url}: {e}")
        return None

def get_cached_content(key, url):
    """Get content from cache or fetch from GitHub"""
    current_time = time.time()
    if key not in cache or current_time - cache['last_fetch'] > CACHE_TIMEOUT:
        content = fetch_from_github(url)
        if content:
            cache[key] = content
            cache['last_fetch'] = current_time
    return cache.get(key, '')

def parse_prices():
    """Parse prices from prices.txt"""
    prices_content = get_cached_content('prices', PRICES_FILE_URL)
    prices = {
        'blender_per_frame': '$0.04',
        'hash_per_minute': '$0.05',
        'tensorflow_base': '$0.10',
        'priority_multiplier': '1.5x',
        'status': 'development'
    }
    
    if prices_content:
        for line in prices_content.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                prices[key.strip().lower()] = value.strip()
    
    return prices

def get_client_info():
    """Get client information from request"""
    return {
        'ip': request.headers.get('X-Forwarded-For', request.remote_addr),
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'referrer': request.headers.get('Referer', 'Direct')
    }

# ===== ROUTES =====
@app.route('/')
def home():
    prices = parse_prices()
    user_count = random.randint(1, 15)
    return render_template('index.html', prices=prices, user_count=user_count)

@app.route('/about')
def about():
    about_content = get_cached_content('about', ABOUT_FILE_URL)
    if not about_content:
        about_content = "# About Our Compute Service\n\nContent loading..."
    return render_template('about.html', content=about_content)

@app.route('/blender-order', methods=['GET', 'POST'])
def blender_order():
    prices = parse_prices()
    
    if request.method == 'POST':
        # Collect form data
        email = request.form.get('email', '').strip()
        project_link = request.form.get('project_link', '').strip()
        bargain = request.form.get('bargain') == 'on'
        priority = request.form.get('priority') == 'on'
        notes = request.form.get('notes', '').strip()
        frame_count = request.form.get('frame_count', '100')
        
        # Calculate price estimate
        base_price = float(prices['blender_per_frame'].replace('$', ''))
        multiplier = 1.5 if priority else 1.0
        estimated_total = f"${base_price * int(frame_count) * multiplier:.2f}"
        
        # Get client info
        client_info = get_client_info()
        
        # Prepare order data
        order_data = {
            'email': email,
            'project_link': project_link,
            'bargain': bargain,
            'priority': priority,
            'notes': notes,
            'frame_count': frame_count,
            'service_type': 'Blender Rendering',
            'base_price': prices['blender_per_frame'],
            'multiplier': f"{multiplier}x",
            'estimated_total': estimated_total,
            'user_ip': client_info['ip'],
            'user_agent': client_info['user_agent'][:100] + '...' if len(client_info['user_agent']) > 100 else client_info['user_agent'],
            'referrer': client_info['referrer']
        }
        
        # Send to Discord
        discord_sent = send_discord_order_notification(order_data)
        
        if discord_sent:
            print(f"✅ Order from {email} sent to Discord")
        else:
            print(f"⚠️ Order from {email} saved locally (Discord failed)")
        
        # Save order locally (in production, save to database)
        save_order_locally(order_data)
        
        return redirect(url_for('order_confirmation', service='blender'))
    
    return render_template('blender_order.html', prices=prices)

def save_order_locally(order_data):
    """Save order to a local JSON file (for backup)"""
    try:
        orders_file = 'orders.json'
        orders = []
        
        if os.path.exists(orders_file):
            with open(orders_file, 'r') as f:
                orders = json.load(f)
        
        orders.append({
            **order_data,
            'timestamp': datetime.now().isoformat(),
            'id': f"ORD-{int(time.time())}"
        })
        
        with open(orders_file, 'w') as f:
            json.dump(orders, f, indent=2)
        
        print(f"✅ Order saved locally: {order_data['email']}")
    except Exception as e:
        print(f"❌ Failed to save order locally: {e}")

@app.route('/order-confirmation/<service>')
def order_confirmation(service):
    return render_template('order_confirmation.html', service=service)

@app.route('/api/order', methods=['POST'])
def api_order():
    """API endpoint for order submissions"""
    try:
        data = request.json
        
        # Add client info
        client_info = get_client_info()
        data.update({
            'user_ip': client_info['ip'],
            'user_agent': client_info['user_agent'],
            'timestamp': datetime.now().isoformat()
        })
        
        # Send to Discord
        success = send_discord_order_notification(data)
        
        if success:
            # Save locally
            save_order_locally(data)
            
            return jsonify({
                'success': True,
                'message': 'Order received and notification sent to Discord',
                'order_id': f"API-{int(time.time())}"
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Order saved locally but Discord notification failed'
            }), 500
            
    except Exception as e:
        print(f"❌ API Order Error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/webhook/test')
def test_webhook():
    """Test the Discord webhook"""
    success = send_discord_test()
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Test message sent to Discord',
            'webhook_url': DISCORD_WEBHOOK_URL[:50] + '...'  # Hide full URL
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to send test message'
        }), 500

@app.route('/webhook/orders')
def view_orders():
    """View saved orders (for admin)"""
    try:
        if os.path.exists('orders.json'):
            with open('orders.json', 'r') as f:
                orders = json.load(f)
            return jsonify({
                'count': len(orders),
                'orders': orders[-10:]  # Last 10 orders
            })
        else:
            return jsonify({'count': 0, 'orders': []})
    except:
        return jsonify({'error': 'Could not load orders'}), 500

@app.route('/api/status')
def api_status():
    """API endpoint for service status"""
    prices = parse_prices()
    return jsonify({
        'status': 'development',
        'message': 'Services under development - Coming soon!',
        'timestamp': datetime.now().isoformat(),
        'prices': prices,
        'user_count': random.randint(1, 15),
        'server_ping': random.randint(20, 80),
        'discord_webhook': 'configured' if DISCORD_WEBHOOK_URL else 'not configured'
    })

@app.route('/api/prices')
def api_prices():
    """API endpoint for current prices"""
    prices = parse_prices()
    return jsonify(prices)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'service': 'pythons-gpus-store',
        'version': '1.2.0',
        'timestamp': datetime.now().isoformat(),
        'discord_webhook': 'active' if DISCORD_WEBHOOK_URL else 'inactive'
    })

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    # Send error to Discord (simplified version)
    error_message = f"""```yaml
🚨 SERVER ERROR
════════════════════════════════════════
• Error: {str(e)}
• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• Path: {request.path}
════════════════════════════════════════
```"""
    
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={
            "content": error_message,
            "username": "Python's GPUS Error Bot"
        }, timeout=5)
    except:
        pass  # Silently fail if Discord is down
    
    return render_template('500.html', error=str(e)), 500

# ===== STARTUP =====
if __name__ == '__main__':
    # Send startup notification
    startup_message = f"""```yaml
🚀 SERVER STARTED
════════════════════════════════════════
• Service: Python's GPUS Store
• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• Port: {os.environ.get('PORT', 5000)}
• Environment: {'Production' if os.environ.get('RENDER') else 'Development'}
════════════════════════════════════════
Discord webhook is ready to receive orders!
```"""
    
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={
            "content": startup_message,
            "username": "Python's GPUS Server"
        }, timeout=5)
        print("✅ Startup notification sent to Discord")
    except Exception as e:
        print(f"⚠️ Could not send startup notification: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
