"""
Agentiqware - Main Application Entry Point
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['PROJECT_ID'] = os.environ.get('GCP_PROJECT_ID', 'agentiqware-dev')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'agentiqware-api'}), 200

@app.route('/api/v1/status', methods=['GET'])
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'operational',
        'version': '1.0.0',
        'environment': os.environ.get('APP_ENV', 'development')
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
