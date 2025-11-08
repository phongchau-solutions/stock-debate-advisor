import requests
import os
from typing import Dict, Any

# Configuration module for zstock

DATA_SOURCE_CONFIG = {
    "VIETCAP": {
        "base_url": "https://trading.vietcap.com.vn",
        "graphql_endpoint": "/data-mt/graphql",
        "ohlc_endpoint": "/api/chart/OHLCChart/gap-chart",
        "headers": {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7,de-DE;q=0.6,de;q=0.5",
            "Connection": "keep-alive",
            "Host": "iq.vietcap.com.vn",
            "Origin": "https://trading.vietcap.com.vn",
            "Referer": "https://trading.vietcap.com.vn/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"142\", \"Google Chrome\";v=\"142\", \"Not_A Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
        },
    }
}

def get_source_config(source: str) -> Dict[str, Any]:
    """
    Get configuration for a specific data source.
    
    Args:
        source: Name of the data source (e.g., 'VIETCAP')
    
    Returns:
        Configuration dictionary for the source
    
    Raises:
        KeyError: If source is not supported
    """
    source = source.upper()
    if source not in DATA_SOURCE_CONFIG:
        raise KeyError(f"Unsupported data source: {source}")
    return DATA_SOURCE_CONFIG[source]

# Fetch configuration for Vietcap
vietcap_config = get_source_config("VIETCAP")
base_url = "https://trading.vietcap.com.vn/iq"
headers = vietcap_config["headers"]

# Directory to save API responses
output_dir = "api_responses"
os.makedirs(output_dir, exist_ok=True)

# List of APIs to test
apis = [
    "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/MBB",
    "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/MBB/financial-statement?section=BALANCE_SHEET",
    "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/MBB/financial-statement/metrics",
    "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/MBB/financial-statement?section=INCOME_STATEMENT",
    "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/MBB/financial-statement?section=CASH_FLOW",
    "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/MBB/financial-statement?section=NOTE",
    "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/MBB/statistics-financial",
    "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/MBB/short-financial?lengthReport=10&lengthReport=10",
    "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/MBB/price-chart?lengthReport=10&toCurrent=true",
    "https://trading.vietcap.com.vn/api/price/symbols/getList",
    "https://trading.vietcap.com.vn/api/price/symbols/getAll",
    "https://iq.vietcap.com.vn/api/iq-insight-service/v1/events/price-board",
    "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/MBB/price-chart?lengthReport=10",
    "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/MBB/technical/ONE_DAY",
    "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company-ratio-daily/MBB?lengthReport=10",
    "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/MBB/financial-data",
]

# Add sentiment news API for MBB
sentiment_news_api = "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/MBB/sentiment-news"

# Add sentiment news crawling for MBB from external sources
external_sources = [
    "https://vietstock.vn/search?q=MBB",
    "https://cafef.vn/search.chn?query=MBB",
    "https://vneconomy.vn/tim-kiem.htm?keyword=MBB",
]

# Test each API
for api in apis:
    print(f"Testing API: {api}")
    try:
        response = requests.get(api, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            # Save response to a text file
            filename = os.path.join(output_dir, api.replace("https://", "").replace("/", "_").replace("?", "_").replace("&", "_") + ".txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Response saved to: {filename}")
        else:
            print(f"Non-200 response: {response.text}")
    except Exception as e:
        print(f"Error testing API {api}: {e}")

# Test the sentiment news API
print(f"Testing API: {sentiment_news_api}")
try:
    response = requests.get(sentiment_news_api, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        # Save response to a text file
        filename = os.path.join(output_dir, "sentiment_news_MBB.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"Response saved to: {filename}")
    else:
        print(f"Non-200 response: {response.text}")
except Exception as e:
    print(f"Error testing API {sentiment_news_api}: {e}")

# Crawl sentiment news from external sources
for source in external_sources:
    print(f"Crawling sentiment news from: {source}")
    try:
        response = requests.get(source, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            # Save response to a text file
            filename = os.path.join(output_dir, source.replace("https://", "").replace("/", "_").replace("?", "_").replace("&", "_") + ".txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Response saved to: {filename}")
        else:
            print(f"Non-200 response: {response.text}")
    except Exception as e:
        print(f"Error crawling sentiment news from {source}: {e}")

# Handle redirect issues for Vietcap APIs
redirect_handling_apis = [
    "https://trading.vietcap.com.vn/api/price/symbols/getList",
    "https://trading.vietcap.com.vn/api/price/symbols/getAll",
]

for api in redirect_handling_apis:
    print(f"Testing API with redirect handling: {api}")
    try:
        response = requests.get(api, headers=headers, allow_redirects=True)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            # Save response to a text file
            filename = os.path.join(output_dir, api.replace("https://", "").replace("/", "_").replace("?", "_").replace("&", "_") + ".txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Response saved to: {filename}")
        else:
            print(f"Non-200 response: {response.text}")
    except Exception as e:
        print(f"Error testing API {api}: {e}")