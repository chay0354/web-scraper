# Google Sheets Setup Instructions

To enable Google Sheets integration, you need to set up Google Cloud credentials:

## Steps:

1. **Create a Google Cloud Project:**
   - Go to https://console.cloud.google.com/
   - Create a new project or select an existing one

2. **Enable Google Sheets API:**
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API" and enable it
   - Also enable "Google Drive API"

3. **Create a Service Account:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Give it a name (e.g., "web-scraper")
   - Click "Create and Continue"
   - Skip the optional steps and click "Done"

4. **Create and Download Key:**
   - Click on the service account you just created
   - Go to the "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose "JSON" format
   - Download the JSON file and save it as `credentials.json` in the project root

5. **Share the Google Sheet:**
   - Open your Google Sheet: https://docs.google.com/spreadsheets/d/1yTXRHCG5VdnK4q_2smRMuGazCgMSnwjbSQpRPnLzCIA/edit
   - Click "Share" button
   - Add the service account email (found in credentials.json, looks like: `your-service-account@project-id.iam.gserviceaccount.com`)
   - Give it "Editor" permissions
   - Click "Send"

6. **Place credentials.json:**
   - Save the downloaded JSON file as `credentials.json` in the project root directory
   - The file should be in the same folder as `browser_scraper.py`

## Note:
- If `credentials.json` is not found, the scraper will still work but will only save to local files (lawyer_names.txt and lawyer_names.xlsx)
- Google Sheets updates will be skipped if credentials are not available
