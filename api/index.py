"""
Vercel serverless function wrapper for the Flask app
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app

# For Vercel, we need to use WSGI
def handler(request):
    """Vercel serverless function handler"""
    return app(request.environ, lambda status, headers: None)

# Also export app directly for compatibility
__all__ = ['app', 'handler']

