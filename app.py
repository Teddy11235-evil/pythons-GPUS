from flask import Flask, render_template, jsonify
import requests
from datetime import datetime
import os

app = Flask(__name__)

# GitHub raw URL for about.txt (replace with your actual GitHub file URL)
ABOUT_FILE_URL = "https://raw.githubusercontent.com/yourusername/yourrepo/main/about.txt"

def get_about_content():
    """Fetch about.txt content from GitHub"""
    try:
        response = requests.get(ABOUT_FILE_URL, timeout=5)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"# About Our Compute Service\n\nUnable to load about information. Error: {str(e)}"

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
        'message': 'Python GPU services are coming up!',
        'timestamp': datetime.now().isoformat(),
        'available_services': ['Python GPU Tasks', 'Data Processing', 'ML Model Training'],
        'pricing_tiers': [
            {'name': 'Basic', 'price': '$0.10/min', 'specs': '1 CPU, 2GB RAM'},
            {'name': 'Pro', 'price': '$0.25/min', 'specs': '2 CPU, 4GB RAM, 1 GPU'},
            {'name': 'Enterprise', 'price': '$0.50/min', 'specs': '4 CPU, 8GB RAM, 2 GPU'}
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
