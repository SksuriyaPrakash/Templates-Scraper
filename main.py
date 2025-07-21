import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Function to create directories if they don't exist
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Function to download a file
def download_file(url, save_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f'Successfully downloaded {url}')
        else:
            print(f'Failed to download {url}')
    except Exception as e:
        print(f'Error downloading {url}: {e}')

# Function to save the HTML file
# def save_html(content, save_path):
#     create_directory(os.path.dirname(save_path))
#     with open(save_path, 'wb') as file:
#         file.write(content)

def save_html(content, save_path):
    directory = os.path.dirname(save_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(save_path, 'wb') as file:
        file.write(content)


# Function to scrape a page
def scrape_page(base_url, url, base_save_path, scraped_pages):
    if url in scraped_pages:
        return
    scraped_pages.add(url)

    response = requests.get(url)
    if response.status_code != 200:
        print(f'Failed to retrieve {url}')
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # Save the HTML file
    parsed_url = urlparse(url)
    path = parsed_url.path if parsed_url.path else 'index.html'
    if path.endswith('/'):
        path += 'index.html'
    html_save_path = os.path.join(base_save_path, path.lstrip('/'))
    save_html(response.content, html_save_path)

    # Download CSS files
    for css in soup.find_all('link', rel='stylesheet'):
        css_url = urljoin(base_url, css['href'])
        css_save_path = os.path.join(base_save_path, urlparse(css_url).path.lstrip('/'))
        create_directory(os.path.dirname(css_save_path))
        download_file(css_url, css_save_path)

    # Download JS files
    for js in soup.find_all('script', src=True):
        js_url = urljoin(base_url, js['src'])
        js_save_path = os.path.join(base_save_path, urlparse(js_url).path.lstrip('/'))
        create_directory(os.path.dirname(js_save_path))
        download_file(js_url, js_save_path)

    # Download images
    for img in soup.find_all('img', src=True):
        img_url = urljoin(base_url, img['src'])
        img_save_path = os.path.join(base_save_path, urlparse(img_url).path.lstrip('/'))
        create_directory(os.path.dirname(img_save_path))
        download_file(img_url, img_save_path)

    # Recursively scrape linked pages
    for link in soup.find_all('a', href=True):
        linked_url = urljoin(base_url, link['href'])
        if urlparse(linked_url).netloc == urlparse(base_url).netloc:
            scrape_page(base_url, linked_url, base_save_path, scraped_pages)

# Main function
def main(base_url, save_path):
    create_directory(save_path)
    scraped_pages = set()
    scrape_page(base_url, base_url, save_path, scraped_pages)

if __name__ == "__main__":
    base_url = 'https://themesbrand.com/steex/layouts/index.html'  # Replace with the URL you want to scrape
    save_path = 'F:/Templates/Ecommerce_dashboard'  # Replace with the path where you want to save the scraped HTML files
    main(base_url,save_path)