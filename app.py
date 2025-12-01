from flask import Flask, render_template, jsonify, request, redirect, url_for
import requests
from datetime import datetime
import os
import random
import time

app = Flask(__name__)

# GitHub URLs for dynamic content
ABOUT_FILE_URL = "https://raw.githubusercontent.com/Teddy11235-evil/pythons-GPUS/main/about.txt"
PRICES_FILE_URL = "https://raw.githubusercontent.com/Teddy11235-evil/pythons-GPUS/main/prices.txt"

# Cache for GitHub content
cache = {
    'prices': {},
    'about': '',
    'last_fetch': 0
}

CACHE_TIMEOUT = 300  # 5 minutes

def fetch_from_github(url):
    """Fetch content from GitHub with caching"""
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
    """Parse prices from prices.txt format"""
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

@app.route('/')
def home():
    prices = parse_prices()
    # Simulate user count (in production, this would come from database)
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
        # Process the form submission
        email = request.form.get('email')
        project_link = request.form.get('project_link')
        bargain = request.form.get('bargain') == 'on'
        priority = request.form.get('priority') == 'on'
        notes = request.form.get('notes', '')
        
        # Calculate price
        base_price = float(prices['blender_per_frame'].replace('$', ''))
        multiplier = 1.5 if priority else 1.0
        
        # In production, save to database and send email
        print(f"Blender Order Received:")
        print(f"Email: {email}")
        print(f"Project: {project_link}")
        print(f"Bargain: {bargain}")
        print(f"Priority: {priority} ({multiplier}x)")
        print(f"Notes: {notes}")
        
        # Redirect to confirmation page
        return redirect(url_for('order_confirmation', service='blender'))
    
    return render_template('blender_order.html', prices=prices)

@app.route('/order-confirmation/<service>')
def order_confirmation(service):
    return render_template('order_confirmation.html', service=service)

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
        'server_ping': random.randint(20, 80)
    })

@app.route('/api/prices')
def api_prices():
    """API endpoint for current prices"""
    prices = parse_prices()
    return jsonify(prices)

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy', 
        'service': 'pythons-gpus-store',
        'version': '1.1.0'
    })

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
