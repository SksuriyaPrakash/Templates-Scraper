import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Function to create directories if they don't exist
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Function to download a file
def download_file(url, save_path, headers):
    try:
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200:
            create_directory(os.path.dirname(save_path))
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f'Successfully downloaded {url}')
        else:
            print(f'Failed to download {url}: Status code {response.status_code}')
    except Exception as e:
        print(f'Error downloading {url}: {e}')

# Function to save the HTML file
def save_html(content, save_path):
    create_directory(os.path.dirname(save_path))
    with open(save_path, 'wb') as file:
        file.write(content)
    print(f'Saved HTML to {save_path}')

# Function to scrape a page
def scrape_page(base_url, url, base_save_path, scraped_pages, headers, use_selenium=False):
    if url in scraped_pages:
        return
    scraped_pages.add(url)

    try:
        if use_selenium:
            # Set up headless Chrome
            options = Options()
            options.add_argument('--headless')
            options.add_argument(f'user-agent={headers["User-Agent"]}')
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(2)  # Wait for JavaScript to load
            content = driver.page_source.encode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            driver.quit()
        else:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f'Failed mullvad Failed to retrieve {url}: Status code {response.status_code}')
                return
            content = response.content
            soup = BeautifulSoup(content, 'html.parser')

        # Save the HTML file
        parsed_url = urlparse(url)
        path = parsed_url.path if parsed_url.path else 'index.html'
        if path.endswith('/'):
            path += 'index.html'
        html_save_path = os.path.join(base_save_path, path.lstrip('/'))
        save_html(content, html_save_path)

        # Download CSS files
        for css in soup.find_all('link', rel='stylesheet'):
            css_url = urljoin(base_url, css.get('href', ''))
            if css_url.endswith('.css'):  # Ensure it's a CSS file
                css_save_path = os.path.join(base_save_path, urlparse(css_url).path.lstrip('/'))
                download_file(css_url, css_save_path, headers)

        # Download JS files
        for js in soup.find_all('script', src=True):
            js_url = urljoin(base_url, js.get('src', ''))
            if js_url.endswith('.js'):  # Ensure it's a JS file
                js_save_path = os.path.join(base_save_path, urlparse(js_url).path.lstrip('/'))
                download_file(js_url, js_save_path, headers)

        # Download images
        for img in soup.find_all('img', src=True):
            img_url = urljoin(base_url, img.get('src', ''))
            if img_url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):  # Ensure it's an image
                img_save_path = os.path.join(base_save_path, urlparse(img_url).path.lstrip('/'))
                download_file(img_url, img_save_path, headers)

        # Recursively scrape linked pages
        for link in soup.find_all('a', href=True):
            linked_url = urljoin(base_url, link['href'])
            if urlparse(linked_url).netloc == urlparse(base_url).netloc:
                scrape_page(base_url, linked_url, base_save_path, scraped_pages, headers, use_selenium)

    except Exception as e:
        print(f'Error scraping {url}: {e}')

# Main function
def main(base_url, save_path, use_selenium=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    create_directory(save_path)
    scraped_pages = set()
    scrape_page(base_url, base_url, save_path, scraped_pages, headers, use_selenium)

if __name__ == "__main__":
    base_url = 'https://dashlite.net/demo9/copywriter/templates-list.html'  # Replace with the correct URL
    save_path = 'G:/template/dashlite'  # Save path
    main(base_url, save_path, use_selenium=True)  # Set use_selenium=True for dynamic content