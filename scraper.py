import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from bs4 import BeautifulSoup

def create_session():
    """Create a requests session with proper headers and retry strategy"""
    session = requests.Session()
    
    # Set proper headers to mimic a real browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    })
    
    # Set up retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def scrape_url(url):
    """Scrape a URL with proper error handling"""
    session = create_session()
    
    try:
        print(f"Attempting to access: {url}")
        
        # Add a small delay to avoid being too aggressive
        time.sleep(2)
        
        response = session.get(url, timeout=30, allow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✓ Successfully accessed the URL")
            return response.text
        else:
            print(f"✗ Received status code: {response.status_code}")
            print(f"Response content: {response.text[:500]}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error accessing URL: {str(e)}")
        return None
    finally:
        session.close()

def parse_html(html_content):
    """Parse HTML content using BeautifulSoup"""
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup
    return None

if __name__ == "__main__":
    url = "https://www.israelbar.biz/"
    
    # Try to scrape the URL
    html_content = scrape_url(url)
    
    if html_content:
        soup = parse_html(html_content)
        if soup:
            print("\n" + "="*50)
            print("Page Title:", soup.title.string if soup.title else "No title found")
            print("="*50)
            
            # Save the HTML to a file
            with open("output.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("\n✓ HTML content saved to output.html")
    else:
        print("\n✗ Failed to retrieve content. The website may be blocking requests.")
        print("\nPossible solutions:")
        print("1. The website may require JavaScript - try using Selenium/Playwright")
        print("2. The website may require cookies/authentication")
        print("3. The website may have IP-based blocking")
        print("4. Check if you need to use a proxy or VPN")

