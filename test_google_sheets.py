"""Test script to verify Google Sheets integration"""
import os
import sys
import io
import gspread
from google.oauth2.service_account import Credentials

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Google Sheets ID
GOOGLE_SHEETS_ID = "1yTXRHCG5VdnK4q_2smRMuGazCgMSnwjbSQpRPnLzCIA"

def test_google_sheets():
    """Test writing to Google Sheets"""
    try:
        # Check for credentials file
        creds_file = os.path.join(os.getcwd(), "credentials.json")
        
        if not os.path.exists(creds_file):
            print("❌ credentials.json not found!")
            print(f"   Expected location: {creds_file}")
            print("\n   Even for public sheets, the Google Sheets API requires authentication to write.")
            print("   You have two options:")
            print("\n   Option 1 (Recommended): Use Service Account")
            print("   1. Follow instructions in GOOGLE_SHEETS_SETUP.md")
            print("   2. Create a service account and download credentials.json")
            print("   3. Share your Google Sheet with the service account email")
            print("\n   Option 2: Make sheet editable by anyone, then use service account")
            print("   (Still requires service account, but sheet can be public)")
            return False
        
        print("✓ Found credentials.json")
        
        # Authenticate
        print("🔐 Authenticating with Google Sheets...")
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(creds_file, scopes=scope)
        client = gspread.authorize(creds)
        print("✓ Authentication successful")
        
        # Open the spreadsheet
        print(f"📊 Opening Google Sheet (ID: {GOOGLE_SHEETS_ID})...")
        sheet = client.open_by_key(GOOGLE_SHEETS_ID)
        worksheet = sheet.sheet1
        print("✓ Sheet opened successfully")
        
        # Get existing data
        try:
            existing_data = worksheet.get_all_values()
            print(f"✓ Found {len(existing_data)} existing rows")
        except:
            existing_data = []
            print("✓ Sheet is empty (new sheet)")
        
        # Prepare test data
        test_row = ["TEST", "Test Area", "123-456-7890", "test@example.com", "Test City"]
        
        # Add headers if sheet is empty
        if len(existing_data) == 0:
            print("📝 Adding headers...")
            headers = [["שם", "התמחות", "טלפון", "מייל", "עיר"]]
            worksheet.append_rows(headers)
            print("✓ Headers added")
        
        # Add test row
        print("📝 Writing test row...")
        worksheet.append_rows([test_row])
        print("✓ Test row written successfully!")
        
        print("\n" + "="*60)
        print("✅ SUCCESS! Google Sheets integration is working!")
        print("="*60)
        print(f"\nYou can check your sheet here:")
        print(f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEETS_ID}/edit")
        print("\nThe test row should appear at the bottom of the sheet.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("🧪 Testing Google Sheets Integration")
    print("="*60)
    print()
    test_google_sheets()
