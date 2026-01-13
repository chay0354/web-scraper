"""Test script to verify scraper's Google Sheets integration works"""
import sys
import io

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import the scraper's Google Sheets function
from browser_scraper import save_details_to_google_sheets

def test_scraper_integration():
    """Test that the scraper's Google Sheets function works"""
    print("="*60)
    print("🧪 Testing Scraper's Google Sheets Integration")
    print("="*60)
    print()
    
    # Create sample lawyer data (like what the scraper would collect)
    sample_lawyers = [
        {
            "name": "Test Lawyer 1",
            "area_of_practice": "מקרקעין/נדל\"ן",
            "phone": "050-1234567",
            "email": "lawyer1@example.com",
            "city": "תל אביב"
        },
        {
            "name": "Test Lawyer 2",
            "area_of_practice": "תיווך",
            "phone": "052-9876543",
            "email": "lawyer2@example.com",
            "city": "ירושלים"
        }
    ]
    
    print(f"📝 Testing with {len(sample_lawyers)} sample lawyers...")
    print()
    
    # Call the same function the scraper uses
    result = save_details_to_google_sheets(sample_lawyers)
    
    if result:
        print()
        print("="*60)
        print("✅ SUCCESS! Scraper's Google Sheets integration works!")
        print("="*60)
        print("\nThe scraper will automatically save data to Google Sheets")
        print("every time it collects lawyer information.")
        return True
    else:
        print()
        print("="*60)
        print("❌ FAILED! Check the error messages above.")
        print("="*60)
        return False

if __name__ == "__main__":
    test_scraper_integration()
