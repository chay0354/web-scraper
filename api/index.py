"""
Vercel serverless function wrapper for the Flask app
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app

# Export Flask app directly - Vercel will handle it as WSGI
# The app variable is what Vercel looks for

