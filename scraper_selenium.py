"""
Alternative scraper using Selenium for JavaScript-heavy websites
or websites with anti-bot protection.
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time

def create_driver(headless=False):
    """Create a Chrome WebDriver instance with proper options"""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless')
    
    # Add options to avoid detection
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Set user agent
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except WebDriverException as e:
        print(f"Error creating Chrome driver: {e}")
        print("Make sure ChromeDriver is installed and in your PATH")
        return None

def scrape_with_selenium(url, wait_time=10):
    """Scrape a URL using Selenium"""
    driver = create_driver(headless=False)  # Set to True for headless mode
    
    if not driver:
        return None
    
    try:
        print(f"Attempting to access: {url}")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Try to wait for a common element (adjust selector as needed)
        try:
            WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            print("Warning: Page took longer than expected to load")
        
        # Get page source
        page_source = driver.page_source
        
        # Get page title
        title = driver.title
        print(f"Page Title: {title}")
        print(f"Page URL: {driver.current_url}")
        
        # Save screenshot for debugging
        driver.save_screenshot("screenshot.png")
        print("✓ Screenshot saved to screenshot.png")
        
        return page_source
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://www.israelbar.biz/"
    
    html_content = scrape_with_selenium(url)
    
    if html_content:
        with open("output_selenium.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("\n✓ HTML content saved to output_selenium.html")
    else:
        print("\n✗ Failed to retrieve content")

