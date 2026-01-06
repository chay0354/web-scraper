"""
Interactive browser scraper that opens a visible browser
and shows what elements are being clicked/pressed.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import re
from datetime import datetime

def create_driver(download_dir=None, headless=True):
    """Create a Chrome WebDriver instance"""
    chrome_options = Options()
    
    # Run in headless mode for server deployment (Vercel)
    if headless:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
    
    # Add options to avoid detection
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--window-size=1920,1080')
    
    if not headless:
        chrome_options.add_argument('--start-maximized')
    
    # Set user agent
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Set up PDF download preferences
    if download_dir is None:
        download_dir = os.path.join(os.getcwd(), "downloads")
    
    # Create download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)
    
    # Configure download preferences
    prefs = {
        "plugins.always_open_pdf_externally": True,  # Download PDFs instead of opening
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    try:
        print("🔧 Setting up ChromeDriver (this may take a moment on first run)...")
        # Use webdriver-manager to automatically download and manage ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✓ ChromeDriver ready")
        print(f"✓ Download directory: {download_dir}")
        return driver
    except WebDriverException as e:
        print(f"✗ Error creating Chrome driver: {e}")
        print("Make sure Chrome browser is installed on your system")
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None

def highlight_element(driver, element, duration=1):
    """Highlight an element with a red border"""
    try:
        # Store original style
        original_style = element.get_attribute('style')
        
        # Highlight with red border
        driver.execute_script(
            "arguments[0].style.border = '3px solid red'; "
            "arguments[0].style.backgroundColor = 'yellow';",
            element
        )
        
        # Wait to see the highlight
        time.sleep(duration)
        
        # Restore original style
        if original_style:
            driver.execute_script(f"arguments[0].style = '{original_style}';", element)
        else:
            driver.execute_script(
                "arguments[0].style.border = ''; "
                "arguments[0].style.backgroundColor = '';",
                element
            )
    except Exception as e:
        print(f"Error highlighting element: {e}")

def click_and_show(driver, element, description="Element"):
    """Click an element and show what was clicked"""
    try:
        print(f"\n🖱️  Clicking: {description}")
        
        # Scroll element into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)
        
        # Highlight before clicking
        highlight_element(driver, element, duration=0.8)
        
        # Get element info
        tag = element.tag_name
        text = element.text[:50] if element.text else "No text"
        element_id = element.get_attribute('id') or "No ID"
        element_class = element.get_attribute('class') or "No class"
        
        print(f"   Tag: {tag}")
        print(f"   Text: {text}")
        print(f"   ID: {element_id}")
        print(f"   Class: {element_class}")
        
        # Click the element
        element.click()
        print(f"   ✓ Clicked successfully!")
        
        # Wait a bit after click
        time.sleep(1)
        
        return True
    except Exception as e:
        print(f"   ✗ Error clicking: {e}")
        return False

def click_close_button(driver):
    """Find and click the close button with class 'close-btn'"""
    print("\n" + "="*60)
    print("🔍 Looking for close button...")
    print("="*60)
    
    try:
        # Try multiple ways to find the close button
        selectors = [
            (By.CLASS_NAME, "close-btn"),
            (By.CSS_SELECTOR, "button.close-btn"),
            (By.XPATH, "//button[contains(@class, 'close-btn')]"),
            (By.XPATH, "//button[contains(@onclick, '__doPostBack') and contains(@class, 'close-btn')]"),
        ]
        
        close_button = None
        for by, selector in selectors:
            try:
                elements = driver.find_elements(by, selector)
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        close_button = elem
                        break
                if close_button:
                    break
            except:
                continue
        
        if close_button:
            print("✓ Found close button!")
            if click_and_show(driver, close_button, "Close Button (סגירה)"):
                print("✓ Close button clicked successfully!")
                time.sleep(2)  # Wait for any popup/modal to close
                return True
            else:
                print("✗ Failed to click close button")
                return False
        else:
            print("⚠ Close button not found (may not be present on this page)")
            return False
            
    except Exception as e:
        print(f"✗ Error finding/clicking close button: {e}")
        return False

def open_business_area_dropdown(driver):
    """Open the business area dropdown"""
    print("\n" + "="*60)
    print("🔍 Opening business area dropdown...")
    print("="*60)
    
    try:
        # Find the dropdown button by ID
        dropdown_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "business-area"))
        )
        
        if dropdown_button:
            print("✓ Found business area dropdown button!")
            if click_and_show(driver, dropdown_button, "Business Area Dropdown (תחומי עיסוק)"):
                print("✓ Dropdown opened!")
                time.sleep(1.5)  # Wait for dropdown to open
                return True
            else:
                print("✗ Failed to open dropdown")
                return False
        else:
            print("✗ Business area dropdown button not found")
            return False
            
    except TimeoutException:
        print("✗ Timeout: Business area dropdown button not found")
        return False
    except Exception as e:
        print(f"✗ Error opening dropdown: {e}")
        return False

def select_business_options(driver):
    """Select the specified business options from the dropdown"""
    print("\n" + "="*60)
    print("🔍 Selecting business options...")
    print("="*60)
    
    # List of options to select (matching exact text from dropdown)
    options_to_select = [
        "מקרקעין/נדל\"ן",  # Fixed: forward slash, not backslash
        "תיווך",
        "אדריכלות",
        "יזמות",
        "ליקויי בניה",
        "מיסוי מקרקעין",
        "שכירות",
        "תיווך",  # Duplicate as per original list
        "הגנת הדייר",
        "חוזים",
        "ירושות, צוואות ועזבונות",  # Fixed: with commas
        "מכרזים",
        "מלונאות",
        "רשויות מקומיות"
    ]
    
    selected_count = 0
    
    try:
        # Wait for dropdown content to be visible
        time.sleep(1.5)
        
        # First, try to find all checkboxes in the dropdown
        try:
            all_checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            print(f"Found {len(all_checkboxes)} checkboxes in dropdown")
        except:
            all_checkboxes = []
        
        # Try to find options by their labels and click the labels (not checkboxes)
        for option_text in options_to_select:
            try:
                found = False
                clickable = None
                
                # Method 1: Find label by text, then click the label (not checkbox)
                # The label will trigger the checkbox click
                selectors = [
                    (By.XPATH, f"//label[normalize-space()='{option_text}']"),
                    (By.XPATH, f"//label[contains(normalize-space(), '{option_text}')]"),
                    (By.XPATH, f"//label[text()='{option_text}']"),
                ]
                
                for by, selector in selectors:
                    try:
                        elements = driver.find_elements(by, selector)
                        for elem in elements:
                            if elem.is_displayed():
                                clickable = elem
                                found = True
                                break
                        if found:
                            break
                    except:
                        continue
                
                # Method 2: Find by checkbox ID and then find its label
                if not found and all_checkboxes:
                    for checkbox in all_checkboxes:
                        try:
                            if not checkbox.is_displayed():
                                continue
                            checkbox_id = checkbox.get_attribute('id')
                            
                            if checkbox_id:
                                try:
                                    label = driver.find_element(By.CSS_SELECTOR, f"label[for='{checkbox_id}']")
                                    if label and label.is_displayed():
                                        label_text = label.text.strip()
                                        # Check if text matches (exact or contains)
                                        if option_text == label_text or option_text in label_text or label_text in option_text:
                                            clickable = label  # Click the label, not checkbox
                                            found = True
                                            break
                                except:
                                    pass
                        except:
                            continue
                
                # Click the found label element
                if clickable and found:
                    print(f"\n   Selecting: {option_text}")
                    highlight_element(driver, clickable, duration=0.5)
                    
                    # Try regular click first
                    try:
                        clickable.click()
                    except Exception as click_error:
                        # If regular click fails, use JavaScript click
                        print(f"   Regular click failed, trying JavaScript click...")
                        try:
                            driver.execute_script("arguments[0].click();", clickable)
                        except Exception as js_error:
                            print(f"   JavaScript click also failed: {js_error}")
                            raise click_error
                    
                    selected_count += 1
                    print(f"   ✓ Selected: {option_text}")
                    time.sleep(0.4)  # Small delay between selections
                else:
                    print(f"   ⚠ Option not found: {option_text}")
                    
            except Exception as e:
                print(f"   ✗ Error selecting '{option_text}': {str(e)[:100]}")  # Truncate long errors
                continue
        
        print(f"\n✓ Successfully selected {selected_count} out of {len(options_to_select)} options")
        time.sleep(1)  # Wait after all selections
        return selected_count
        
    except Exception as e:
        print(f"✗ Error in select_business_options: {e}")
        import traceback
        traceback.print_exc()
        return selected_count

def click_search_button(driver):
    """Click the search button"""
    print("\n" + "="*60)
    print("🔍 Clicking search button...")
    print("="*60)
    
    try:
        # Find the search button by ID
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "cmdSearch"))
        )
        
        if search_button:
            print("✓ Found search button!")
            if click_and_show(driver, search_button, "Search Button (חיפוש)"):
                print("✓ Search button clicked successfully!")
                time.sleep(3)  # Wait for search results to load
                return True
            else:
                print("✗ Failed to click search button")
                return False
        else:
            print("✗ Search button not found")
            return False
            
    except TimeoutException:
        print("✗ Timeout: Search button not found")
        return False
    except Exception as e:
        print(f"✗ Error clicking search button: {e}")
        return False

def extract_lawyer_cards(driver):
    """Extract all lawyer cards with names and detail links from the current page"""
    print("\n" + "="*60)
    print("📋 Extracting lawyer cards from current page...")
    print("="*60)
    
    lawyer_cards = []
    
    try:
        # Find all lawyer result items
        result_items = driver.find_elements(By.CSS_SELECTOR, "div.lawyers-search-results_item, .lawyers-search-results_item")
        
        print(f"Found {len(result_items)} lawyer cards on this page")
        
        for item in result_items:
            try:
                # Get the name
                try:
                    name_elem = item.find_element(By.CSS_SELECTOR, "div.lawyers-search-results_item-title h3, h3")
                    hebrew_name = name_elem.text.split('\n')[0].strip() if name_elem.text else ""
                    
                    # Get the English name (from span)
                    try:
                        span = name_elem.find_element(By.TAG_NAME, "span")
                        english_name = span.text.strip() if span else ""
                    except:
                        english_name = ""
                    
                    # Combine both names
                    if english_name:
                        full_name = f"{hebrew_name} ({english_name})"
                    else:
                        full_name = hebrew_name
                except:
                    full_name = ""
                
                # Get the detail link
                detail_link = None
                try:
                    link_elem = item.find_element(By.CSS_SELECTOR, "a[href*='lawyer-fd']")
                    detail_link = link_elem.get_attribute("href")
                except:
                    pass
                
                if full_name:
                    lawyer_cards.append({
                        "name": full_name,
                        "hebrew_name": hebrew_name,
                        "english_name": english_name,
                        "detail_link": detail_link
                    })
                    print(f"   ✓ {full_name}")
                    
            except Exception as e:
                print(f"   ⚠ Error extracting card: {e}")
                continue
        
        print(f"\n✓ Extracted {len(lawyer_cards)} cards from this page")
        return lawyer_cards
        
    except Exception as e:
        print(f"✗ Error extracting cards: {e}")
        import traceback
        traceback.print_exc()
        return lawyer_cards

def extract_lawyer_details(driver, detail_url, results_url):
    """Extract detailed information from a lawyer's detail page"""
    details = {
        "name": "",
        "area_of_practice": "",
        "phone": "",
        "email": "",
        "city": ""
    }
    
    try:
        # Navigate to detail page
        driver.get(detail_url)
        time.sleep(2)  # Wait for page to load
        
        # Extract name - look for h1 or title
        try:
            name_elem = driver.find_element(By.CSS_SELECTOR, "h1, .lawyer-name, [class*='name'], .title")
            details["name"] = name_elem.text.strip()
        except:
            pass
        
        # Extract area of practice (תחום עיסוק)
        try:
            # Find span with title "תחום עיסוק" and get the value
            practice_label = driver.find_element(By.XPATH, "//span[@class='title' and contains(text(), 'תחום עיסוק')]")
            # Get the next sibling or parent's next span
            practice_elem = practice_label.find_element(By.XPATH, "./following-sibling::span | ../span[2]")
            details["area_of_practice"] = practice_elem.text.strip()
        except:
            try:
                # Alternative: find by text content
                practice_elem = driver.find_element(By.XPATH, "//span[contains(text(), 'תחום עיסוק')]/following-sibling::span")
                details["area_of_practice"] = practice_elem.text.strip()
            except:
                pass
        
        # Extract phone (טלפון נייד)
        try:
            phone_label = driver.find_element(By.XPATH, "//span[@class='title' and contains(text(), 'טלפון נייד')]")
            phone_elem = phone_label.find_element(By.XPATH, "./following-sibling::span | ../span[2]")
            details["phone"] = phone_elem.text.strip()
        except:
            try:
                phone_elem = driver.find_element(By.XPATH, "//span[contains(text(), 'טלפון נייד')]/following-sibling::span")
                details["phone"] = phone_elem.text.strip()
            except:
                pass
        
        # Extract email (דוא"ל)
        try:
            email_label = driver.find_element(By.XPATH, "//span[@class='title' and contains(text(), 'דוא\"ל')]")
            email_elem = email_label.find_element(By.XPATH, "./following-sibling::span | ../span[2] | ./following-sibling::a")
            details["email"] = email_elem.text.strip()
            if not details["email"]:
                email_href = email_elem.get_attribute("href")
                if email_href and "mailto:" in email_href:
                    details["email"] = email_href.replace("mailto:", "")
        except:
            try:
                # Try mailto link
                email_elem = driver.find_element(By.CSS_SELECTOR, "a[href^='mailto:']")
                email_href = email_elem.get_attribute("href")
                if email_href:
                    details["email"] = email_href.replace("mailto:", "")
            except:
                pass
        
        # Extract city (ישוב)
        try:
            city_label = driver.find_element(By.XPATH, "//span[@class='title' and contains(text(), 'ישוב')]")
            city_elem = city_label.find_element(By.XPATH, "./following-sibling::span | ../span[2]")
            details["city"] = city_elem.text.strip()
        except:
            try:
                city_elem = driver.find_element(By.XPATH, "//span[contains(text(), 'ישוב')]/following-sibling::span")
                details["city"] = city_elem.text.strip()
            except:
                pass
        
        # Go back to results page
        driver.get(results_url)
        time.sleep(2)
        
        return details
        
    except Exception as e:
        print(f"   ⚠ Error extracting details: {e}")
        # Try to go back to results page even on error
        try:
            driver.get(results_url)
            time.sleep(2)
        except:
            pass
        return details

def get_next_page_button(driver):
    """Find and return the next page button"""
    try:
        # Look for the next page button
        next_button = driver.find_element(By.CSS_SELECTOR, "a.nav-btn.next")
        if next_button and next_button.is_displayed() and "disabled" not in next_button.get_attribute("class"):
            return next_button
    except:
        pass
    
    # Also try finding by text or aria-label
    try:
        next_button = driver.find_element(By.XPATH, "//a[@class='nav-btn next' and not(contains(@class, 'disabled'))]")
        if next_button and next_button.is_displayed():
            return next_button
    except:
        pass
    
    return None

def navigate_to_next_page(driver):
    """Navigate to the next page of results"""
    try:
        next_button = get_next_page_button(driver)
        
        if next_button:
            print("\n➡️  Navigating to next page...")
            highlight_element(driver, next_button, duration=0.5)
            next_button.click()
            time.sleep(3)  # Wait for page to load
            return True
        else:
            print("\n⚠ No next page button found (reached last page)")
            return False
            
    except Exception as e:
        print(f"✗ Error navigating to next page: {e}")
        return False

def get_total_pages(driver):
    """Get the total number of pages from pagination"""
    try:
        # Find all page number links
        page_links = driver.find_elements(By.CSS_SELECTOR, "a.nav-btn.last, a.num")
        
        # Try to find the last page number
        last_page_link = driver.find_element(By.CSS_SELECTOR, "a.nav-btn.last")
        if last_page_link:
            href = last_page_link.get_attribute("href")
            if href and "chunckStart=" in href:
                # Extract the chunk start value
                match = re.search(r'chunckStart=(\d+)', href)
                if match:
                    last_chunk = int(match.group(1))
                    # Assuming 20 results per page (based on chunckStart increments)
                    total_pages = (last_chunk // 20) + 1
                    return total_pages
        
        # Fallback: count page number links
        page_nums = driver.find_elements(By.CSS_SELECTOR, "a.num")
        if page_nums:
            return len(page_nums)
        
        return None
    except:
        return None

def extract_all_lawyer_details(driver, max_names=None, max_pages=None, resume_from_page=1, existing_count=0):
    """Extract lawyer details from all pages by visiting each detail page"""
    print("\n" + "="*60)
    print("📚 Starting to extract lawyer details from all pages...")
    print("="*60)
    
    if resume_from_page > 1:
        print(f"🔄 Resuming from page {resume_from_page} (already have {existing_count} lawyers)")
    
    if max_names:
        remaining = max_names - existing_count
        if remaining > 0:
            print(f"🎯 Target: Extract {remaining} more lawyer details (total target: {max_names})")
        else:
            print(f"✓ Already reached target of {max_names} lawyers")
            return []
    if max_pages:
        print(f"📄 Maximum pages: {max_pages}")
    
    all_details = []
    current_page = resume_from_page
    original_url = driver.current_url
    
    # Load existing names to avoid duplicates
    existing_names = set()
    try:
        existing_lawyers = load_details_from_file("lawyer_names.txt")
        existing_names = {lawyer.get('name', '').strip() for lawyer in existing_lawyers if lawyer.get('name')}
        print(f"📋 Loaded {len(existing_names)} existing names to avoid duplicates")
    except:
        pass
    
    # If resuming, navigate to the correct page first
    if resume_from_page > 1:
        print(f"\n➡️  Navigating to page {resume_from_page}...")
        for page in range(2, resume_from_page + 1):
            if not navigate_to_next_page(driver):
                print(f"⚠ Could not navigate to page {page}")
                break
            original_url = driver.current_url
            time.sleep(2)
    
    # Get total pages if possible
    total_pages = get_total_pages(driver)
    if total_pages:
        print(f"📄 Total pages available: {total_pages}")
    
    while True:
        print(f"\n{'='*60}")
        print(f"📄 Page {current_page}")
        print(f"{'='*60}")
        
        # Extract lawyer cards (names and links) from current page
        lawyer_cards = extract_lawyer_cards(driver)
        
        # Process each lawyer card
        for i, card in enumerate(lawyer_cards, 1):
            # Check if we've reached the limit
            if max_names and len(all_details) >= max_names:
                print(f"\n✓ Reached target of {max_names} lawyers")
                break
            
            print(f"\n   [{len(all_details) + 1}/{max_names if max_names else '?'}] Processing: {card['name']}")
            
            # If we have a detail link, visit it
            if card['detail_link']:
                print(f"   🔗 Opening detail page...")
                details = extract_lawyer_details(driver, card['detail_link'], original_url)
                
                # Use name from card if detail page doesn't have it
                if not details['name']:
                    details['name'] = card['name']
                
                all_details.append(details)
                print(f"   ✓ Extracted: {details['name']}")
                print(f"      תחום עיסוק: {details['area_of_practice'] or 'N/A'}")
                print(f"      טלפון: {details['phone'] or 'N/A'}")
                print(f"      מייל: {details['email'] or 'N/A'}")
                print(f"      עיר: {details['city'] or 'N/A'}")
            else:
                # No detail link, just save the name
                details = {
                    "name": card['name'],
                    "area_of_practice": "",
                    "phone": "",
                    "email": "",
                    "city": ""
                }
                all_details.append(details)
                print(f"   ⚠ No detail link found, saved name only")
            
            # Save to file every 10 names (for both cases)
            if len(all_details) % 10 == 0:
                print(f"\n💾 Saving batch of 10 lawyers to file...")
                filepath = os.path.join(os.getcwd(), "lawyer_names.txt")
                is_first_batch = not os.path.exists(filepath) or os.path.getsize(filepath) == 0
                save_details_to_file(all_details[-10:], append=not is_first_batch, page_num=current_page)
        
        print(f"\n📊 Total details collected so far: {len(all_details)}")
        
        # Check if we've reached the name limit
        if max_names and len(all_details) >= max_names:
            print(f"\n✓ Reached target of {max_names} lawyers")
            break
        
        # Check if we should continue (page limit)
        if max_pages and current_page >= max_pages:
            print(f"\n✓ Reached maximum page limit ({max_pages})")
            break
        
        # Try to navigate to next page
        if not navigate_to_next_page(driver):
            print("\n✓ Reached the last page")
            break
        
        # Update original_url for next page
        original_url = driver.current_url
        current_page += 1
        
        # Safety limit
        if current_page > 1000:
            print("\n⚠ Safety limit reached (1000 pages)")
            break
    
    # Trim to exact limit if needed
    if max_names and len(all_details) > max_names:
        all_details = all_details[:max_names]
        print(f"\n✓ Trimmed to exactly {max_names} lawyers")
    
    return all_details

def save_details_to_file(details_list, filename="lawyer_names.txt", append=False, page_num=None):
    """Save extracted lawyer details to a text file in the specified format"""
    try:
        filepath = os.path.join(os.getcwd(), filename)
        mode = "a" if append else "w"
        
        with open(filepath, mode, encoding="utf-8") as f:
            # Write page header if provided
            if page_num is not None:
                f.write(f"page{page_num}:\n")
            
            for details in details_list:
                f.write(f"שם: {details.get('name', '')}\n")
                f.write(f"התמכות: {details.get('area_of_practice', '')}\n")
                f.write(f"טלפון: {details.get('phone', '')}\n")
                f.write(f"מייל: {details.get('email', '')}\n")
                f.write(f"עיר: {details.get('city', '')}\n")
                f.write("\n")  # Empty line between entries
        
        action = "Appended" if append else "Saved"
        page_info = f" (page {page_num})" if page_num else ""
        print(f"\n✓ {action} {len(details_list)} lawyer details{page_info} to: {filepath}")
        return filepath
    except Exception as e:
        print(f"✗ Error saving details to file: {e}")
        return None

def get_last_page_from_file(filename="lawyer_names.txt"):
    """Get the last page number from the file"""
    try:
        filepath = os.path.join(os.getcwd(), filename)
        if not os.path.exists(filepath):
            return 0
        
        last_page = 0
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("page") and ":" in line:
                    try:
                        page_num = int(line.split("page")[1].split(":")[0])
                        last_page = max(last_page, page_num)
                    except:
                        pass
        
        return last_page
    except:
        return 0

def count_lawyers_in_file(filename="lawyer_names.txt"):
    """Count how many lawyers are already in the file"""
    try:
        filepath = os.path.join(os.getcwd(), filename)
        if not os.path.exists(filepath):
            return 0
        
        count = 0
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("שם:"):
                    count += 1
        
        return count
    except:
        return 0

def load_details_from_file(filename="lawyer_names.txt"):
    """Load lawyer details from file and return as list"""
    try:
        filepath = os.path.join(os.getcwd(), filename)
        if not os.path.exists(filepath):
            return []
        
        details_list = []
        current_detail = {}
        
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("שם:"):
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
        print(f"✗ Error loading details from file: {e}")
        return []

def click_print_and_download_pdf(driver, download_dir=None):
    """Click the print button and download the PDF"""
    print("\n" + "="*60)
    print("🖨️  Clicking print button and downloading PDF...")
    print("="*60)
    
    if download_dir is None:
        download_dir = os.path.join(os.getcwd(), "downloads")
    
    try:
        # Find the print button
        print_button = None
        selectors = [
            (By.CSS_SELECTOR, "button.btn-print"),
            (By.CSS_SELECTOR, "button[class*='print']"),
            (By.XPATH, "//button[contains(@class, 'btn-print')]"),
            (By.XPATH, "//button[.//span[contains(@class, 'icon-print')]]"),
        ]
        
        for by, selector in selectors:
            try:
                elements = driver.find_elements(by, selector)
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        print_button = elem
                        break
                if print_button:
                    break
            except:
                continue
        
        if not print_button:
            print("✗ Print button not found")
            return False
        
        print("✓ Found print button!")
        
        # Highlight and click the print button
        highlight_element(driver, print_button, duration=0.8)
        print_button.click()
        print("✓ Print button clicked!")
        
        # Wait for print dialog to appear
        print("⏳ Waiting for print dialog to open...")
        time.sleep(3)
        
        # Try to interact with Chrome's print dialog using keyboard navigation
        # Since the dialog is a native browser UI, we use keyboard shortcuts
        try:
            print("📄 Interacting with print dialog...")
            
            # The print dialog should already be open
            # We need to:
            # 1. Navigate to the destination dropdown
            # 2. Select "Save as PDF" 
            # 3. Click the Save button
            
            actions = ActionChains(driver)
            
            # Wait a moment for dialog to fully load
            time.sleep(1)
            
            # Method: Use keyboard navigation to interact with print dialog
            # First, try to focus on the destination dropdown
            # In Chrome's print dialog, the destination is usually the first focusable element
            print("   Focusing on destination dropdown...")
            
            # Press Tab to navigate (destination dropdown is usually first or second element)
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.3)
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.3)
            
            # Open the dropdown with Space or Enter
            print("   Opening destination dropdown...")
            actions.send_keys(Keys.SPACE).perform()
            time.sleep(0.5)
            
            # "Save as PDF" is usually the second option (index 1)
            # Navigate to it if not already selected
            print("   Ensuring 'Save as PDF' is selected...")
            # Press Arrow Down once to go to "Save as PDF" (if not already there)
            actions.send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(0.3)
            # Press Enter to select it
            actions.send_keys(Keys.ENTER).perform()
            time.sleep(0.5)
            
            # Now navigate to the Save button
            # Usually need to Tab a few times or press Enter
            print("   Navigating to Save button...")
            # Tab to Save button (usually 2-3 tabs)
            for i in range(3):
                actions.send_keys(Keys.TAB).perform()
                time.sleep(0.2)
            
            # Press Enter to click Save
            print("   Clicking Save button...")
            actions.send_keys(Keys.ENTER).perform()
            time.sleep(2)
            
            print("✓ PDF download initiated!")
            print(f"✓ Check your downloads folder: {download_dir}")
            return True
            
        except Exception as dialog_error:
            print(f"⚠ Dialog interaction failed: {dialog_error}")
            print("Trying CDP method as fallback...")
            
            # Fallback: Use Chrome DevTools Protocol to print to PDF directly
            try:
                print("📄 Generating PDF using Chrome's print-to-PDF (CDP)...")
                
                # Get the current page URL for filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_filename = f"search_results_{timestamp}.pdf"
                pdf_path = os.path.join(download_dir, pdf_filename)
                
                # Use CDP to print to PDF
                result = driver.execute_cdp_cmd("Page.printToPDF", {
                    "printBackground": True,
                    "paperWidth": 8.5,
                    "paperHeight": 11,
                    "marginTop": 0,
                    "marginBottom": 0,
                    "marginLeft": 0,
                    "marginRight": 0
                })
                
                # Save the PDF
                import base64
                pdf_data = base64.b64decode(result['data'])
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_data)
                
                print(f"✓ PDF saved to: {pdf_path}")
                return True
                
            except Exception as cdp_error:
                print(f"✗ CDP method also failed: {cdp_error}")
                print("⚠ Please manually save the PDF from the print dialog")
                print("   The dialog should be open - select 'Save as PDF' and click Save")
                return False
        
    except Exception as e:
        print(f"✗ Error in print/download process: {e}")
        import traceback
        traceback.print_exc()
        return False

def find_and_click_links(driver, max_links=5):
    """Find and click clickable links/buttons on the page"""
    print("\n" + "="*60)
    print("🔍 Searching for clickable elements...")
    print("="*60)
    
    clicked_count = 0
    
    # Find all clickable elements
    selectors = [
        (By.TAG_NAME, "a"),           # Links
        (By.TAG_NAME, "button"),      # Buttons
        (By.CSS_SELECTOR, "input[type='submit']"),  # Submit buttons
        (By.CSS_SELECTOR, "[onclick]"),  # Elements with onclick
        (By.CSS_SELECTOR, "[role='button']"),  # ARIA buttons
    ]
    
    all_elements = []
    for by, selector in selectors:
        try:
            elements = driver.find_elements(by, selector)
            for elem in elements:
                if elem.is_displayed() and elem.is_enabled():
                    all_elements.append(elem)
        except:
            pass
    
    # Remove duplicates
    seen = set()
    unique_elements = []
    for elem in all_elements:
        try:
            elem_id = id(elem)
            if elem_id not in seen:
                seen.add(elem_id)
                unique_elements.append(elem)
        except:
            pass
    
    print(f"\nFound {len(unique_elements)} clickable elements")
    print(f"Will click up to {max_links} elements\n")
    
    for i, element in enumerate(unique_elements[:max_links], 1):
        try:
            text = element.text.strip()[:30] if element.text else f"Element {i}"
            description = f"{i}. {text}"
            
            if click_and_show(driver, element, description):
                clicked_count += 1
                
            # Small delay between clicks
            time.sleep(1)
            
        except Exception as e:
            print(f"   ✗ Error with element {i}: {e}")
            continue
    
    print(f"\n✓ Successfully clicked {clicked_count} elements")
    return clicked_count

def interactive_scraper(url, headless=True):
    """Main scraper function that opens browser and shows interactions"""
    driver = create_driver(headless=headless)
    
    if not driver:
        return None
    
    try:
        print("="*60)
        print("🌐 Opening browser...")
        print("="*60)
        print(f"URL: {url}")
        
        # Navigate to URL
        driver.get(url)
        print("✓ Page loaded")
        
        # Wait for page to load
        time.sleep(3)
        
        # Get page info
        print("\n" + "="*60)
        print("📄 Page Information")
        print("="*60)
        print(f"Title: {driver.title or 'No title'}")
        print(f"Current URL: {driver.current_url}")
        print(f"Page Source Length: {len(driver.page_source)} characters")
        
        # Save initial screenshot
        driver.save_screenshot("screenshot_initial.png")
        print("\n✓ Initial screenshot saved to screenshot_initial.png")
        
        # Click the close button first (if it exists)
        click_close_button(driver)
        
        # Wait a bit after closing
        time.sleep(1)
        
        # Open business area dropdown
        if open_business_area_dropdown(driver):
            # Select business options
            selected = select_business_options(driver)
            
            # Save screenshot after selections
            if selected > 0:
                driver.save_screenshot("screenshot_after_selections.png")
                print("\n✓ Screenshot after selections saved to screenshot_after_selections.png")
            
            # Click search button
            if click_search_button(driver):
                # Wait for search results to load
                time.sleep(3)
                
                # Extract all lawyer details (visiting each detail page)
                # Check if we need to resume
                existing_count = count_lawyers_in_file("lawyer_names.txt")
                last_page = get_last_page_from_file("lawyer_names.txt")
                resume_from = last_page if last_page > 0 else 1
                
                if existing_count > 0:
                    print(f"\n📊 Found {existing_count} existing lawyers in file (last page: {last_page})")
                    print(f"🔄 Will resume from page {resume_from}")
                
                # Note: Details are saved every 10 names automatically
                # No limit - will scrape all available lawyers
                all_details = extract_all_lawyer_details(driver, max_names=None, resume_from_page=resume_from, existing_count=existing_count)
                
                # Final verification
                if all_details:
                    print(f"\n💾 Final summary: {len(all_details)} total lawyers saved to lawyer_names.txt")
                else:
                    print("\n⚠ No details were extracted")
        
        # Find and click other elements (optional - comment out if not needed)
        # clicked = find_and_click_links(driver, max_links=5)
        
        # Save final screenshot
        driver.save_screenshot("screenshot_final.png")
        print("\n✓ Final screenshot saved to screenshot_final.png")
        
        # Save page source
        with open("output_browser.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("✓ HTML content saved to output_browser.html")
        
        print("\n" + "="*60)
        print("✅ Scraping complete!")
        print("="*60)
        
        if not headless:
            print("\nBrowser will stay open for 10 seconds so you can see the result...")
            print("Close the browser window or wait for it to close automatically.")
            # Keep browser open for viewing
            time.sleep(10)
        
        return driver.page_source
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        print("\nClosing browser...")
        driver.quit()

if __name__ == "__main__":
    url = "https://www.israelbar.biz/"
    
    print("\n" + "="*60)
    print("🚀 Interactive Browser Scraper")
    print("="*60)
    print("\nThis scraper will:")
    print("1. Open Chrome browser (headless mode)")
    print("2. Navigate to the website")
    print("3. Extract lawyer names from search results")
    print("4. Navigate through pages automatically")
    print("5. Save names to lawyer_names.txt")
    print("\n" + "="*60 + "\n")
    
    # Run in headless mode (set to False if you want to see the browser)
    html_content = interactive_scraper(url, headless=True)
    
    if html_content:
        print("\n✓ Scraping completed successfully!")
    else:
        print("\n✗ Scraping failed")

