from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class VietcapClient:
    """Lightweight client for Vietcap data (trading.vietcap.com.vn preferred).

    Defaults to the GraphQL + OHLC endpoints used by Vietcap's trading site:
    - Base URL: https://trading.vietcap.com.vn
    - GraphQL: /data-mt/graphql
    - OHLC:    /api/chart/OHLCChart/gap-chart

    Backward-compatible REST paths (api.vietcap.com.vn) remain available but may be gated.
    Endpoints can be overridden via constructor args or environment variables.
    """

    # Large GraphQL query copied from reference (ref/zstock) to fetch financial ratios
    _GQL_COMPANY_FINANCIAL_RATIO = (
        """
        fragment Ratios on CompanyFinancialRatio {
          ticker
          yearReport
          lengthReport
          updateDate
          revenue
          revenueGrowth
          netProfit
          netProfitGrowth
          ebitMargin
          roe
          roic
          roa
          pe
          pb
          eps
          currentRatio
          cashRatio
          quickRatio
          interestCoverage
          ae
          netProfitMargin
          grossMargin
          ev
          issueShare
          ps
          pcf
          bvps
          evPerEbitda
          BSA1
          BSA2
          BSA5
          BSA8
          BSA10
          BSA159
          BSA16
          BSA22
          BSA23
          BSA24
          BSA162
          BSA27
          BSA29
          BSA43
          BSA46
          BSA50
          BSA209
          BSA53
          BSA54
          BSA55
          BSA56
          BSA58
          BSA67
          BSA71
          BSA173
          BSA78
          BSA79
          BSA80
          BSA175
          BSA86
          BSA90
          BSA96
          CFA21
          CFA22
          at
          fat
          acp
          dso
          dpo
          ccc
          de
          le
          ebitda
          ebit
          dividend
          RTQ10
          charterCapitalRatio
          RTQ4
          epsTTM
          charterCapital
          fae
          RTQ17
          CFA26
          CFA6
          CFA9
          BSA85
          CFA36
          BSB98
          BSB101
          BSA89
          CFA34
          CFA14
          ISB34
          ISB27
          ISA23
          ISS152
          ISA102
          CFA27
          CFA12
          CFA28
          BSA18
          BSB102
          BSB110
          BSB108
          CFA23
          ISB41
          BSB103
          BSA40
          BSB99
          CFA16
          CFA18
          CFA3
          ISB30
          BSA33
          ISB29
          CFS200
          ISA2
          CFA24
          BSB105
          CFA37
          ISS141
          BSA95
          CFA10
          ISA4
          BSA82
          CFA25
          BSB111
          ISI64
          BSB117
          ISA20
          CFA19
          ISA6
          ISA3
          BSB100
          ISB31
          ISB38
          ISB26
          BSA210
          CFA20
          CFA35
          ISA17
          ISS148
          BSB115
          ISA9
          CFA4
          ISA7
          CFA5
          ISA22
          CFA8
          CFA33
          CFA29
          BSA30
          BSA84
          BSA44
          BSB107
          ISB37
          ISA8
          BSB109
          ISA19
          ISB36
          ISA13
          ISA1
          BSB121
          ISA14
          BSB112
          ISA21
          ISA10
          CFA11
          ISA12
          BSA15
          BSB104
          BSA92
          BSB106
          BSA94
          ISA18
          CFA17
          ISI87
          BSB114
          ISA15
          BSB116
          ISB28
          BSB97
          CFA15
          ISA11
          ISB33
          BSA47
          ISB40
          ISB39
          CFA7
          CFA13
          ISS146
          ISB25
          BSA45
          BSB118
          CFA1
          CFS191
          ISB35
          CFB65
          CFA31
          BSB113
          ISB32
          ISA16
          CFS210
          BSA48
          BSA36
          ISI97
          CFA30
          CFA2
          CFB80
          CFA38
          CFA32
          ISA5
          BSA49
          CFB64
          __typename
        }

        query Query($ticker: String!, $period: String!) {
          CompanyFinancialRatio(ticker: $ticker, period: $period) {
            ratio {
              ...Ratios
              __typename
            }
            period
            __typename
          }
        }
        """
    )

    def __init__(
        self,
        base_url: Optional[str] = None,
        balance_path: Optional[str] = None,
        price_path: Optional[str] = None,
        indexes_path: Optional[str] = None,
        graphql_endpoint: Optional[str] = None,
        ohlc_endpoint: Optional[str] = None,
        timeout: float = 20.0,
    ):
        # Prefer trading.vietcap GraphQL by default
        self.base_url = (base_url or os.environ.get("VIETCAP_API_BASE", "https://trading.vietcap.com.vn")).rstrip("/")

        # REST fallbacks (api.vietcap.com.vn); retained for compatibility
        self.balance_path = balance_path or os.environ.get("VIETCAP_BALANCE_PATH", "/market/balance-sheet")
        self.price_path = price_path or os.environ.get("VIETCAP_PRICE_PATH", "/market/stocks")
        self.indexes_path = indexes_path or os.environ.get("VIETCAP_INDEXES_PATH", "/market/indices")

        # GraphQL + OHLC endpoints used by the trading site
        self.graphql_endpoint = graphql_endpoint or os.environ.get("VIETCAP_GRAPHQL_ENDPOINT", "/data-mt/graphql")
        self.ohlc_endpoint = ohlc_endpoint or os.environ.get("VIETCAP_OHLC_ENDPOINT", "/api/chart/OHLCChart/gap-chart")

        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        # Use a desktop UA to avoid basic bot filters
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Referer": "https://trading.vietcap.com.vn/",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{path}"
        logger.debug("GET %s params=%s", url, params)
        resp = requests.get(url, headers=self._headers(), params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, json: Dict[str, Any]) -> Any:
        url = f"{self.base_url}{path}"
        logger.debug("POST %s json=%s", url, json)
        resp = requests.post(url, headers=self._headers(), json=json, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    # ---------------------------
    # GraphQL-backed operations
    # ---------------------------
    def _use_graphql(self) -> bool:
        # Heuristic: use GraphQL if base_url points to trading host
        return "trading.vietcap.com.vn" in self.base_url

    def get_balance_sheet(
        self,
        ticker: str,
        period: str = "quarterly",
        limit: int = 8,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Fetch financial ratios and statements.

        When using GraphQL, this fetches CompanyFinancialRatio for the ticker and period.
        Fallback: uses legacy REST balance sheet path if base_url is not the trading host.
        """
        if self._use_graphql():
            gql_period = "Q" if period.lower().startswith("q") else "Y"
            payload: Dict[str, Any] = {
                "query": self._GQL_COMPANY_FINANCIAL_RATIO,
                "variables": {"ticker": ticker, "period": gql_period},
            }
            data = self._post(self.graphql_endpoint, json=payload)
            return {"ticker": ticker, "period": period, "data": data}

        # REST fallback
        params: Dict[str, Any] = {"ticker": ticker, "period": period, "limit": limit}
        if extra_params:
            params.update(extra_params)
        data = self._get(self.balance_path, params=params)
        return {"ticker": ticker, "period": period, "data": data}

    def get_prices(
        self,
        ticker: str,
        range_: str = "1y",
        interval: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Fetch OHLC price series.

        On trading host, uses OHLC POST endpoint with timeFrame/countBack/to.
        Fallback: legacy REST prices endpoint with range/interval params.
        """
        if self._use_graphql():
            # Map interval to Vietcap OHLC timeframe
            interval_map = {"1d": "ONE_DAY", "1m": "ONE_MINUTE", "1w": "ONE_WEEK"}
            timeframe = interval_map.get((interval or "1d").lower(), "ONE_DAY")

            # Simple range -> countBack mapping
            def _count_back(r: str) -> int:
                r = (r or "1y").lower()
                try:
                    if r.endswith("y"):
                        return max(1, int(r[:-1]) * 365)
                    if r.endswith("m"):
                        return max(1, int(r[:-1]) * 30)
                    if r.endswith("w"):
                        return max(1, int(r[:-1]) * 7)
                    if r.endswith("d"):
                        return max(1, int(r[:-1]))
                except ValueError:
                    pass
                return 365

            payload: Dict[str, Any] = {
                "timeFrame": timeframe,
                "symbols": [ticker],
                "countBack": _count_back(range_),
                "to": int(time.time()),
            }
            # extra_params ignored here because the OHLC endpoint expects fixed keys
            data = self._post(self.ohlc_endpoint, json=payload)
            return {"ticker": ticker, "range": range_, "interval": interval, "data": data}

        # REST fallback
        params: Dict[str, Any] = {"ticker": ticker, "range": range_}
        if interval:
            params["interval"] = interval
        if extra_params:
            params.update(extra_params)
        data = self._get(self.price_path, params=params)
        return {"ticker": ticker, "range": range_, "interval": interval, "data": data}

    def get_indexes(self, codes: List[str], extra_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetch market index data.
        
        Uses OHLC endpoint for supported indices (VNINDEX, VN30), 
        falls back to REST endpoint for others.
        """
        if self._use_graphql():
            # Use OHLC endpoint for supported Vietnamese indices
            results = {}
            for code in codes:
                try:
                    # Get 1 month of daily data for each index
                    ohlc_result = self.get_prices(code, range_='1m', interval='1d')
                    if 'data' in ohlc_result and ohlc_result['data']:
                        results[code] = ohlc_result['data']
                    else:
                        results[code] = {"error": f"No data available for {code}"}
                except Exception as e:
                    results[code] = {"error": str(e)}
            
            return {"codes": codes, "data": results}
        
        # REST fallback (may not work but kept for compatibility)
        params: Dict[str, Any] = {"codes": ",".join(codes)}
        if extra_params:
            params.update(extra_params)
        data = self._get(self.indexes_path, params=params)
        return {"codes": codes, "data": data}
