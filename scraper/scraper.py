import requests
from bs4 import BeautifulSoup
import os
import re
from scraper.pdf_handler import extract_text_from_mixed_pdf
from urllib.parse import urljoin, urlparse
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
# Function to scrape a webpage and find all links and PDFs
def scrape_website(url, visited=None, depth=0, max_depth=2):
    if visited is None:
        visited = set()

    # Avoid revisiting the same URL
    if url in visited or depth > max_depth:
        return "", []

    visited.add(url)

    print(f"Scraping {url}...")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return "", []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract text from the webpage
    text = soup.get_text(separator=' ', strip=True)

    # Find all links in the page
    pdf_links = []
    all_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # Check if it's a PDF link
        if href.endswith('.pdf'):
            pdf_links.append(urljoin(url, href))
        else:
            # Ensure we only follow internal links (same domain)
            href = urljoin(url, href)  # Convert relative URL to absolute

            # Filter out repetitive links like "/sitemap////"
            if is_valid_url(href, url):
                all_links.append(href)

    # Recursively scrape all found links
    for link in all_links:
        sub_text, sub_pdfs = scrape_website(link, visited, depth+1, max_depth)
        text += sub_text
        pdf_links += sub_pdfs

    return text, pdf_links

# Helper function to validate URLs
def is_valid_url(link, base_url):
    # Check if the link belongs to the same domain
    if not link.startswith(base_url):
        return False
    
    # Avoid links with repeated slashes (e.g., "sitemap///")
    if re.search(r'\/{2,}', urlparse(link).path):
        return False

    return True

# Function to download and process a PDF (including OCR)
def download_pdf(pdf_url):
    print(f"Downloading PDF {pdf_url}...")

    try:
        # Ensure the 'temp_pdfs' directory exists
        if not os.path.exists('temp_pdfs'):
            os.makedirs('temp_pdfs')

        response = requests.get(pdf_url, headers=headers)
        response.raise_for_status()
        pdf_path = os.path.join('temp_pdfs', os.path.basename(pdf_url))

        with open(pdf_path, 'wb') as f:
            f.write(response.content)

        # Extract text from the PDF (with OCR if necessary)
        pdf_text = extract_text_from_mixed_pdf(pdf_path)
        return pdf_path, pdf_text

    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF {pdf_url}: {e}")
        return None, ""

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, ""

