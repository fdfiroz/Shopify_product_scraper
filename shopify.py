import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse
import json

def ensure_files_exist():
    # Create progress.json if it doesn't exist
    if not os.path.exists('progress.json'):
        with open('progress.json', 'w') as f:
            json.dump({}, f)
    
    # Create urls.txt if it doesn't exist
    if not os.path.exists('urls.txt'):
        with open('urls.txt', 'w') as f:
            f.write("# Add your Shopify collection URLs here (one per line)\n")
        print("Please add URLs to urls.txt file before running the script")
        exit(1)

def load_progress():
    try:
        with open('progress.json', 'r') as f:
            content = f.read()
            return json.loads(content) if content else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Ensure required files exist
ensure_files_exist()

# Configure Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

try:
    driver = webdriver.Chrome(options=chrome_options)
except Exception as e:
    print(f"Error initializing Chrome driver: {str(e)}")
    print("Make sure Chrome and chromedriver are properly installed")
    exit(1)

# Set a longer page load timeout (in seconds)
driver.set_page_load_timeout(180)

# Read collection URLs from urls.txt
try:
    with open("urls.txt", "r") as f:
        collection_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not collection_urls:
        print("No URLs found in urls.txt. Please add some URLs first.")
        driver.quit()
        exit(1)
except FileNotFoundError:
    print("urls.txt file not found")
    driver.quit()
    exit(1)

# Load progress
progress = load_progress()

# Filter out already processed URLs
collection_urls = [url for url in collection_urls if url not in progress]

all_data = []

# Loop through each collection URL
for collection_url in collection_urls:
    # Each collection uses pagination; format the URL accordingly
    base_url = f"{collection_url}?page={{}}"
    
    # Navigate to the first page to extract category and total pages
    try:
        driver.get(base_url.format(1))
    except TimeoutException:
        print(f"Timeout loading {base_url.format(1)}. Attempting to stop loading.")
        driver.execute_script("window.stop();")
    time.sleep(3)  # Wait for the page to load
    
    # Extract collection category from header
    try:
        category = driver.find_element(By.CSS_SELECTOR, "h1.section-header__title").text.strip()
    except Exception as e:
        category = None
    
    # Determine total pages by inspecting pagination links
    pagination_links = driver.find_elements(By.CSS_SELECTOR, "div.pagination span.page a")
    total_pages = 1
    if pagination_links:
        pages = []
        for link in pagination_links:
            text = link.text.strip()
            if text.isdigit():
                pages.append(int(text))
        if pages:
            total_pages = max(pages)
    print(f"Processing collection: {collection_url}")
    print(f"Category: {category}, Total pages: {total_pages}")
    
    # Loop through each page in the current collection
    for page in range(1, total_pages + 1):
        page_url = base_url.format(page)
        try:
            driver.get(page_url)
        except TimeoutException:
            print(f"Timeout loading {page_url}. Attempting to stop loading.")
            driver.execute_script("window.stop();")
        time.sleep(3)  # Wait for page load
        
        # Scroll to the bottom to trigger lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Find all product elements on the page
        products = driver.find_elements(By.CSS_SELECTOR, "div.grid-product__content")
        
        for product in products:
            # Extract image URL (first check 'src', then fallback to 'data-srcset')
            try:
                image = product.find_element(By.CSS_SELECTOR, "img.grid__image-contain")
                image_src = image.get_attribute("src")
                if not image_src or "placeholder" in image_src.lower():
                    data_srcset = image.get_attribute("data-srcset")
                    if data_srcset:
                        image_src = data_srcset.split(",")[-1].strip().split(" ")[0]
            except Exception as e:
                image_src = None
            
            # Fix image URL if it starts with '//' by prepending 'https:'
            if image_src and image_src.startswith("//"):
                image_src = "https:" + image_src
            
            # Extract product title
            try:
                title = product.find_element(By.CSS_SELECTOR, "div.grid-product__title").text.strip()
            except Exception as e:
                title = None
            
            # Extract product link as full URL
            try:
                product_link = product.find_element(By.CSS_SELECTOR, "a.grid-product__link").get_attribute("href")
            except Exception as e:
                product_link = None
            
            # Extract current price
            try:
                current_price = product.find_element(By.CSS_SELECTOR, "span.grid-product__price").text.strip()
            except Exception as e:
                current_price = None
            
            # Extract original price
            try:
                original_price = product.find_element(By.CSS_SELECTOR, "span.grid-product__price--original").text.strip()
            except Exception as e:
                original_price = None
            
            # Extract discount (using XPath to find any span containing a dash)
            try:
                discount = product.find_element(By.XPATH, ".//span[contains(text(),'-')]").text.strip()
            except Exception as e:
                discount = None
            
            all_data.append({
                "category": category,
                "page": page,
                "image": image_src,
                "name": title,
                "link": product_link,
                "current_price": current_price,
                "original_price": original_price,
                "discount": discount
            })
        
        # Save the cumulative data to an Excel file immediately after processing each page
        df = pd.DataFrame(all_data)
        df.to_excel("products.xlsx", index=False)
        print(f"Collection {collection_url} Page {page} processed and saved to Excel.")
        
        # After saving to Excel, update progress
        progress[collection_url] = len(all_data)
        with open('progress.json', 'w') as f:
            json.dump(progress, f)

driver.quit()
