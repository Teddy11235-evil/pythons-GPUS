from flask import Flask, render_template, jsonify
import requests
from datetime import datetime
import os

app = Flask(__name__)

# Updated with your actual GitHub URL
ABOUT_FILE_URL = "https://raw.githubusercontent.com/Teddy11235-evil/pythons-GPUS/main/about.txt"

def get_about_content():
    """Fetch about.txt content from GitHub"""
    try:
        response = requests.get(ABOUT_FILE_URL, timeout=5)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"# About Our Compute Service\n\nUnable to load about information. Please check the GitHub file exists.\n\nError: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    about_content = get_about_content()
    return render_template('about.html', content=about_content)

@app.route('/api/status')
def api_status():
    """API endpoint for service status"""
    return jsonify({
        'status': 'operational',
        'message': 'Python GPU services are online! Ready for compute tasks.',
        'timestamp': datetime.now().isoformat(),
        'stats': {
            'projects_completed': 5,
            'uptime': '99.8%',
            'response_time': '45ms'
        }
    })

@app.route('/api/services')
def api_services():
    """API endpoint for available services"""
    return jsonify({
        'services': [
            {
                'name': 'Blender Rendering',
                'price': '$0.04 per frame',
                'description': 'High-quality 3D rendering with Blender',
                'status': 'available',
                'icon': 'fas fa-cube'
            },
            {
                'name': 'TensorFlow GPU Compute',
                'price': 'Starting at $0.10/min',
                'description': 'TensorFlow machine learning tasks',
                'status': 'available',
                'icon': 'fas fa-brain'
            },
            {
                'name': 'Hash Cracking',
                'price': '$0.05 per minute',
                'description': 'GPU-accelerated hash cracking',
                'status': 'available',
                'icon': 'fas fa-lock'
            },
            {
                'name': 'Hosting',
                'price': 'Currently unavailable',
                'description': 'Coming soon - check back later',
                'status': 'unavailable',
                'icon': 'fas fa-server'
            }
        ]
    })

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy', 'service': 'pythons-gpus-store'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
