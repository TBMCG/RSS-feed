import sys
import os

# Add the root directory to the path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app
from flask_sqlalchemy import SQLAlchemy
from models import db
import json

# Initialize database
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

def handler(event, context):
    """Netlify function handler for Flask app"""
    try:
        # Convert Netlify event to WSGI environ
        environ = {
            'REQUEST_METHOD': event.get('httpMethod', 'GET'),
            'PATH_INFO': event.get('path', '/'),
            'QUERY_STRING': event.get('queryStringParameters', ''),
            'CONTENT_TYPE': event.get('headers', {}).get('content-type', ''),
            'CONTENT_LENGTH': str(len(event.get('body', ''))),
            'HTTP_HOST': event.get('headers', {}).get('host', ''),
            'wsgi.input': event.get('body', ''),
            'wsgi.errors': sys.stderr,
            'wsgi.version': (1, 0),
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
        }
        
        # Add headers to environ
        for key, value in event.get('headers', {}).items():
            key = 'HTTP_' + key.upper().replace('-', '_')
            environ[key] = value
        
        response_data = []
        def start_response(status, headers):
            response_data.append({'status': status, 'headers': headers})
        
        # Call Flask app
        response = app(environ, start_response)
        
        # Convert WSGI response to Netlify format
        body = b''.join(response).decode('utf-8')
        
        return {
            'statusCode': int(response_data[0]['status'].split()[0]),
            'headers': dict(response_data[0]['headers']),
            'body': body
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }