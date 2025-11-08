from typing import Dict, Any
import requests


class FundamentalAnalysis:
    def __init__(self, base_url: str, headers: Dict[str, str]):
        self.base_url = base_url
        self.headers = headers

    def fetch_balance_sheet(self) -> Dict[str, Any]:
        endpoint = "financial-statement?section=BALANCE_SHEET"
        return self._fetch_data(endpoint)

    def fetch_income_statement(self) -> Dict[str, Any]:
        endpoint = "financial-statement?section=INCOME_STATEMENT"
        return self._fetch_data(endpoint)

    def fetch_cash_flow(self) -> Dict[str, Any]:
        endpoint = "financial-statement?section=CASH_FLOW"
        return self._fetch_data(endpoint)

    def fetch_financial_data(self) -> Dict[str, Any]:
        endpoint = "financial-data"
        return self._fetch_data(endpoint)

    def _fetch_data(self, endpoint: str) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data from {url}: {response.status_code}")


class TechnicalAnalysis:
    def __init__(self, base_url: str, headers: Dict[str, str]):
        self.base_url = base_url
        self.headers = headers

    def fetch_price_chart(self) -> Dict[str, Any]:
        endpoint = "price-chart?lengthReport=10"
        return self._fetch_data(endpoint)

    def fetch_technical_one_day(self) -> Dict[str, Any]:
        endpoint = "technical/ONE_DAY"
        return self._fetch_data(endpoint)

    def _fetch_data(self, endpoint: str) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data from {url}: {response.status_code}")