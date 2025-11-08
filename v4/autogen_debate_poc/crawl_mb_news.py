import os
from bs4 import BeautifulSoup
import requests
from datetime import datetime

# Define the URLs to scrape
news_urls = [
    "https://vietstock.vn/search?q=MBB",
    "https://cafef.vn/tim-kiem.chn?keywords=MBB",
    "https://finance.vietstock.vn/MBB/tin-moi-nhat.htm",
    "https://vneconomy.vn/tim-kiem.html?Text=MBB",
]

# Output directory for saving news content
output_dir = "mbb_news"
os.makedirs(output_dir, exist_ok=True)

# Function to scrape news content
def scrape_news(url):
    print(f"Scraping news from: {url}")
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract all paragraph text as an example
            paragraphs = soup.find_all('p')
            content = "\n".join(p.get_text() for p in paragraphs)
            return content
        else:
            print(f"Failed to scrape {url}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

# Crawl and save news content
for url in news_urls:
    content = scrape_news(url)
    if content:
        # Generate a filename based on the URL and timestamp
        filename = os.path.join(output_dir, f"{url.split('//')[-1].replace('/', '_').replace('?', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved content to: {filename}")
    else:
        print(f"No content scraped from: {url}")