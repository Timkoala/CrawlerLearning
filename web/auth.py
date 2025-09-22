from flask import Flask, request, jsonify
from functools import wraps
import os

def require_api_key(f):
    """Decorator to require API key for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if not api_key or api_key != os.environ.get('API_KEY', 'default-key'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def validate_json(f):
    """Decorator to validate JSON in request"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        return f(*args, **kwargs)
    return decorated_function