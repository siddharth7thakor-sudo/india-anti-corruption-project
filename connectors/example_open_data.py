"""
Example Open Data Connector - data.gov.in
India Anti-Corruption Project - Dynamic Data Layer

This connector demonstrates a live pull from the Government of India
Open Government Data Platform (data.gov.in). It uses the official
datagovindia Python library.

Install dependencies:
    pip install requests datagovindia pandas

Set environment variable:
    export DATAGOVINDIA_API_KEY="your_api_key_here"

Resources:
    - data.gov.in: https://data.gov.in/
    - datagovindia docs: https://econabhishek.github.io/datagovindia_blog.html
    - API Setu: https://www.apisetu.gov.in/
"""

import os
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from datagovindia import DataGovIndia  # type: ignore
    DATAGOVINDIA_AVAILABLE = True
except ImportError:
    DATAGOVINDIA_AVAILABLE = False
    DataGovIndia = None  # type: ignore

import requests

from connectors.base import http_get, BaseConnector, HttpError


# =============================================================================
# DATA.GOV.IN CONNECTOR
# =============================================================================

class OpenDataConnector(BaseConnector):
    """
    Connector for the Indian Government Open Data Platform.
    Performs live pulls from data.gov.in APIs.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.data.gov.in/resource/"
    ):
        super().__init__(base_url, api_key)
        self.client = None
        if DATAGOVINDIA_AVAILABLE:
            self._init_client()

    def _init_client(self) -> None:
        """Initialize the datagovindia client."""
        key = self.api_key or os.environ.get("DATAGOVINDIA_API_KEY")
        if not key:
            raise RuntimeError(
                "Set DATAGOVINDIA_API_KEY in environment or pass api_key"
            )
        self.client = DataGovIndia(key)

    def fetch_dataset(
        self,
        api_index: str,
        results_per_req: int = 50,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Live pull from a data.gov.in API resource.

        Every call hits the live API and fetches the latest data.

        Args:
            api_index: The index_name of the dataset from data.gov.in
            results_per_req: Number of results to fetch per request (default: 50)
            filters: Optional filter parameters

        Returns:
            List of records as dicts

        Example API indices (find on data.gov.in):
            - Budget datasets
            - Subsidy scheme datasets
            - GST / tax datasets
            - Public procurement datasets

        Raises:
            RuntimeError: If API key is missing or library not installed
        """
        if not DATAGOVINDIA_AVAILABLE:
            raise ImportError(
                "datagovindia not installed. Run: pip install datagovindia"
            )

        if self.client is None:
            self._init_client()

        data = self.client.get_api_data(
            api_index=api_index,
            results_per_req=results_per_req,
            filter_by=filters or {}
        )

        # Convert to list of dicts
        records = data.to_dict(orient="records")
        return records

    def fetch_raw_json(
        self,
        api_index: str,
        results_per_req: int = 50,
    ) -> Dict[str, Any]:
        """
        Fetch raw JSON response from data.gov.in API.

        Useful for debugging or when you need full response metadata.
        """
        if not DATAGOVINDIA_AVAILABLE:
            raise ImportError("datagovindia not installed")

        if self.client is None:
            self._init_client()

        data = self.client.get_api_data(
            api_index=api_index,
            results_per_req=results_per_req
        )
        return json.loads(data.to_json())


def fetch_sample_dataset(
    api_index: str,
    results_per_req: int = 50,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Convenience function for quick live pulls from data.gov.in.

    This is the main entry point for your fraud detection pipeline.

    Args:
        api_index: dataset index from data.gov.in catalog
        results_per_req: number of rows to fetch
        filters: optional filter dict

    Returns:
        List of records

    Usage:
        >>> from connectors.example_open_data import fetch_sample_dataset
        >>> records = fetch_sample_dataset("your_api_index", results_per_req=10)
        >>> for row in records[:3]:
        ...     print(row)
    """
    connector = OpenDataConnector()
    return connector.fetch_dataset(
        api_index=api_index,
        results_per_req=results_per_req,
        filters=filters
    )


# =============================================================================
# DIRECT HTTP CONNECTOR (for endpoints without datagovindia wrapper)
# =============================================================================

def fetch_direct_api(
    url: str,
    api_key: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Direct HTTP fetch from any government API that returns JSON.

    Use this when datagovindia doesn't support your target endpoint,
    or for other government portals that expose JSON APIs directly.

    Args:
        url: Full URL of the API endpoint
        api_key: Optional API key (sent as query param 'api-key')
        params: Additional query parameters

    Returns:
        Parsed JSON response as dict

    Examples:
        # Central dataset catalog
        >>> data = fetch_direct_api(
        ...     "https://api.data.gov.in/resource/catalog",
        ...     api_key="your_key"
        ... )

        # Union Budget data
        >>> data = fetch_direct_api(
        ...     "https://unionbudget.gov.in/api/v1/expenditure",
        ...     params={"year": "2025-26", "ministry": "Railways"}
        ... )
    """
    headers = {}
    if api_key:
        if params is None:
            params = {}
        params["api-key"] = api_key

    resp = http_get(url, params=params, headers=headers)
    return resp.json()


# =============================================================================
# REUSABLE PATTERN FOR OTHER GOVERNMENT PORTALS
# =============================================================================

class GenericGovPortalConnector(BaseConnector):
    """
    Generic connector pattern for any government portal.
    Inherit from this class and override fetch_data() for each new portal.

    To use for a new portal (e.g., MCA, PMAY, Sanchar Saathi):

    1. Create a new file: connectors/mca.py
    2. Define: class MCAConnector(GenericGovPortalConnector)
    3. Override fetch_data() with portal-specific logic
    4. Use http_get() from base.py for live HTTP calls
    """

    def __init__(
        self,
        base_url: str,
        portal_name: str,
        api_key: Optional[str] = None
    ):
        super().__init__(base_url, api_key)
        self.portal_name = portal_name

    def fetch_data(
        self,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Override this method in each portal-specific connector.
        Should perform a live HTTP GET and return parsed data.
        """
        raise NotImplementedError(
            f"Subclass {self.portal_name} must implement fetch_data()"
        )

    def is_available(self) -> bool:
        """
        Check if the portal endpoint is accessible.
        Returns True if a live GET returns HTTP 200.
        """
        try:
            resp = requests.get(self.base_url, timeout=10)
            return resp.status_code == 200
        except Exception:
            return False
