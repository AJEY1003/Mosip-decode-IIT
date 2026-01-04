#!/usr/bin/env python3
"""
Simple launcher for the MOSIP ITR Assistant backend
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from flask import Flask
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'message': 'MOSIP ITR Assistant Backend is running'}
    
    @app.route('/')
    def home():
        return {
            'message': 'MOSIP ITR Assistant Backend API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'docs': '/api/docs'
            }
        }
    
    if __name__ == '__main__':
        print("Starting MOSIP ITR Assistant Backend...")
        print("Backend will be available at: http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
        
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Please install required packages:")
    print("pip install flask flask-cors")
    sys.exit(1)