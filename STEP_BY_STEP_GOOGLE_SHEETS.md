# Step-by-Step: Google Sheets Setup

Follow these steps exactly to enable Google Sheets integration:

## Step 1: Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. If you're not signed in, sign in with your Google account
3. Click the project dropdown at the top (next to "Google Cloud")
4. Click "New Project"
5. Enter project name: `web-scraper` (or any name you like)
6. Click "Create"
7. Wait a few seconds for the project to be created
8. Make sure the new project is selected (check the dropdown at the top)

## Step 2: Enable Google Sheets API

1. In the left sidebar, click "APIs & Services" > "Library"
2. In the search box at the top, type: `Google Sheets API`
3. Click on "Google Sheets API" in the results
4. Click the blue "ENABLE" button
5. Wait for it to enable (you'll see a checkmark)
6. Go back to "APIs & Services" > "Library"
7. Search for: `Google Drive API`
8. Click on "Google Drive API"
9. Click the blue "ENABLE" button
10. Wait for it to enable

## Step 3: Create Service Account

1. In the left sidebar, click "APIs & Services" > "Credentials"
2. At the top, click "Create Credentials"
3. Select "Service Account" from the dropdown
4. In the "Service account name" field, type: `web-scraper`
5. Click "Create and Continue"
6. Skip "Grant this service account access to project" (click "Continue")
7. Skip "Grant users access to this service account" (click "Done")

## Step 4: Create and Download Key

1. You should now see your service account in the list (named "web-scraper")
2. Click on the service account name (web-scraper)
3. Click the "KEYS" tab at the top
4. Click "ADD KEY" > "Create new key"
5. Select "JSON" (it should be selected by default)
6. Click "CREATE"
7. A JSON file will automatically download to your computer
8. **IMPORTANT:** Note the email address shown on this page (it looks like: `web-scraper@your-project-id.iam.gserviceaccount.com`)
   - You'll need this email in the next step!

## Step 5: Share Google Sheet with Service Account

1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1yTXRHCG5VdnK4q_2smRMuGazCgMSnwjbSQpRPnLzCIA/edit
2. Click the green "Share" button in the top right
3. In the "Add people and groups" field, paste the service account email (from Step 4)
   - It looks like: `web-scraper@your-project-id.iam.gserviceaccount.com`
4. Make sure "Editor" is selected (not Viewer)
5. **UNCHECK** "Notify people" (you don't need to notify a service account)
6. Click "Share" button
7. You should see a message that the service account was added

## Step 6: Place credentials.json File

1. Find the JSON file that downloaded in Step 4
   - It's usually in your Downloads folder
   - The filename will be something like: `your-project-id-abc123.json`
2. Copy this file to your project folder: `C:\projects\web-scraper\`
3. Rename the file to exactly: `credentials.json`
   - Make sure it's `credentials.json` (not `credentials.json.txt`)
   - The file should be in the same folder as `browser_scraper.py`

## Step 7: Test It!

1. Open PowerShell in your project folder
2. Run: `python test_google_sheets.py`
3. You should see: "✅ SUCCESS! Google Sheets integration is working!"
4. Check your Google Sheet - you should see a test row added!

## Troubleshooting

**If you get "credentials.json not found":**
- Make sure the file is named exactly `credentials.json` (not `credentials.json.txt`)
- Make sure it's in `C:\projects\web-scraper\` folder
- Check that Windows isn't hiding file extensions (the file should show as just `credentials.json`)

**If you get "Permission denied" or "Access denied":**
- Make sure you shared the Google Sheet with the service account email (Step 5)
- Make sure you gave it "Editor" permissions (not Viewer)

**If you get "API not enabled":**
- Go back to Step 2 and make sure both APIs are enabled:
  - Google Sheets API
  - Google Drive API

## That's It!

Once `test_google_sheets.py` works, your scraper will automatically write to Google Sheets every time it saves data!
