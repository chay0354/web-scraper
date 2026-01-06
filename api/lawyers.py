"""
Vercel serverless function for lawyers API
"""
from server import app

def handler(request):
    """Vercel serverless function handler"""
    return app(request.environ, lambda status, headers: None)

