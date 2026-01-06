# Lawyer Scraper & API Server

A web scraper that extracts lawyer information from israelbar.biz and serves it via a REST API.

## Features

- Scrapes lawyer details (name, area of practice, phone, email, city)
- Automatically resumes from where it stopped
- Saves data every 10 lawyers
- Organizes data by pages
- RESTful API to access the data
- Ready for Vercel deployment

## Local Development

### Setup

```bash
pip install -r requirements.txt
```

### Run the Server

```bash
python server.py
```

The server will:
- Start on http://localhost:5000
- Automatically run the scraper in the background
- Resume from where it stopped (if any data exists)

### Run Scraper Only

```bash
python browser_scraper.py
```

## API Endpoints

- `GET /api/lawyers` - Get all lawyer data
- `GET /api/lawyers/<id>` - Get specific lawyer by index
- `GET /api/stats` - Get statistics about the data
- `GET /api/scraper/status` - Get scraper status and progress
- `POST /api/scraper/start` - Manually start the scraper

## Vercel Deployment

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. The app will be deployed and the scraper will run automatically.

## Notes

- The scraper runs in headless mode (no visible browser)
- Data is saved to `lawyer_names.txt` with page headers
- The scraper automatically resumes from the last page
- ChromeDriver is managed automatically via webdriver-manager

## File Structure

```
lawyer_names.txt - Contains scraped data with page headers:
  page1:
  שם: [name]
  התמכות: [area]
  ...
```
