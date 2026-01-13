"""
Flask server to serve lawyer data via GET requests
Also runs the scraper automatically
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os
import json
import threading
from browser_scraper import interactive_scraper, count_lawyers_in_file, get_last_page_from_file

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global flag to track if scraper is running
scraper_running = False
scraper_thread = None

def load_details_from_file(filename="lawyer_names.txt"):
    """Load lawyer details from file and return as list (handles page headers)"""
    try:
        filepath = os.path.join(os.getcwd(), filename)
        if not os.path.exists(filepath):
            return []
        
        details_list = []
        current_detail = {}
        
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip page headers like "page1:"
                if line.startswith("page") and line.endswith(":"):
                    continue
                elif line.startswith("שם:"):
                    if current_detail:  # Save previous detail
                        details_list.append(current_detail)
                    current_detail = {"name": line.replace("שם:", "").strip()}
                elif line.startswith("התמכות:"):
                    current_detail["area_of_practice"] = line.replace("התמכות:", "").strip()
                elif line.startswith("טלפון:"):
                    current_detail["phone"] = line.replace("טלפון:", "").strip()
                elif line.startswith("מייל:"):
                    current_detail["email"] = line.replace("מייל:", "").strip()
                elif line.startswith("עיר:"):
                    current_detail["city"] = line.replace("עיר:", "").strip()
                elif line == "" and current_detail:
                    # Empty line indicates end of entry
                    if current_detail:
                        details_list.append(current_detail)
                        current_detail = {}
            
            # Add last detail if exists
            if current_detail:
                details_list.append(current_detail)
        
        return details_list
    except Exception as e:
        print(f"Error loading details from file: {e}")
        return []

@app.route('/api/lawyers', methods=['GET'])
def get_all_lawyers():
    """Get all lawyer data"""
    # On Vercel, start scraper on first API call if not running
    import os
    if os.getenv('VERCEL') == '1' and not scraper_running:
        run_scraper_on_startup()
    
    lawyers = load_details_from_file()
    return jsonify({
        "success": True,
        "count": len(lawyers),
        "data": lawyers
    })

@app.route('/api/lawyers/<int:lawyer_id>', methods=['GET'])
def get_lawyer_by_id(lawyer_id):
    """Get a specific lawyer by index"""
    lawyers = load_details_from_file()
    if 0 <= lawyer_id < len(lawyers):
        return jsonify({
            "success": True,
            "data": lawyers[lawyer_id]
        })
    else:
        return jsonify({
            "success": False,
            "error": f"Lawyer with ID {lawyer_id} not found. Total lawyers: {len(lawyers)}"
        }), 404

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about the lawyer data"""
    lawyers = load_details_from_file()
    return jsonify({
        "success": True,
        "total_lawyers": len(lawyers),
        "with_email": sum(1 for l in lawyers if l.get('email')),
        "with_phone": sum(1 for l in lawyers if l.get('phone')),
        "with_city": sum(1 for l in lawyers if l.get('city')),
        "with_area": sum(1 for l in lawyers if l.get('area_of_practice'))
    })

@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        "message": "Lawyer Data API",
        "endpoints": {
            "GET /api/lawyers": "Get all lawyers",
            "GET /api/lawyers/<id>": "Get lawyer by index",
            "GET /api/stats": "Get statistics",
            "GET /api/scraper/status": "Get scraper status",
            "POST /api/scraper/start": "Start the scraper"
        }
    })

@app.route('/api/scraper/status', methods=['GET'])
def scraper_status():
    """Get scraper status"""
    existing_count = count_lawyers_in_file()
    last_page = get_last_page_from_file()
    return jsonify({
        "success": True,
        "running": scraper_running,
        "lawyers_collected": existing_count,
        "last_page": last_page
    })

@app.route('/api/scraper/start', methods=['POST', 'GET'])
def start_scraper():
    """Start the scraper in background"""
    global scraper_running, scraper_thread
    
    if scraper_running:
        return jsonify({
            "success": False,
            "message": "Scraper is already running"
        }), 400
    
    def run_scraper():
        global scraper_running
        scraper_running = True
        try:
            url = "https://www.israelbar.biz/"
            # Starting from lawyer #20,000 (handled in browser_scraper.py)
            interactive_scraper(url, headless=True)
        except Exception as e:
            print(f"Scraper error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            scraper_running = False
    
    scraper_thread = threading.Thread(target=run_scraper, daemon=True)
    scraper_thread.start()
    
    return jsonify({
        "success": True,
        "message": "Scraper started in background"
    })

def run_scraper_on_startup():
    """Run scraper automatically when server starts"""
    global scraper_running, scraper_thread
    
    def run_scraper():
        global scraper_running
        scraper_running = True
        try:
            url = "https://www.israelbar.biz/"
            print("\n" + "="*60)
            print("🤖 Auto-starting scraper...")
            print("="*60)
            interactive_scraper(url, headless=True)
        except Exception as e:
            print(f"Scraper error: {e}")
        finally:
            scraper_running = False
    
    scraper_thread = threading.Thread(target=run_scraper, daemon=True)
    scraper_thread.start()

# For Vercel, we need to export the app
# The scraper will run in background when deployed

if __name__ == '__main__':
    # Fix encoding for Windows console
    import sys
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("="*60)
    print("🚀 Starting Lawyer Data Server")
    print("="*60)
    print("\nAvailable endpoints:")
    print("  GET /api/lawyers - Get all lawyer data")
    print("  GET /api/lawyers/<id> - Get specific lawyer by index")
    print("  GET /api/stats - Get statistics")
    print("  GET /api/scraper/status - Get scraper status")
    print("  POST /api/scraper/start - Start scraper manually")
    print("\nServer starting on http://localhost:5000")
    print("="*60 + "\n")
    
    # Start scraper automatically (only in local development)
    import os
    if os.getenv('VERCEL') != '1':
        run_scraper_on_startup()
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

