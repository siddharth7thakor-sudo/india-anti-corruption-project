"""
Base HTTP connector for live government data pulls.
India Anti-Corruption Project - Dynamic Data Layer

This module provides a reusable HTTP GET helper that hits live government
endpoints every time it runs. Used by all connectors in this package.

Usage:
    from connectors.base import http_get, HttpError
    response = http_get("https://data.gov.in/api/...")
    data = response.json()
"""

import os
import logging
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class HttpError(Exception):
    """Raised when an HTTP request fails."""
    pass


class BaseConnector:
    """
    Base class for all government portal connectors.
    Provides common functionality for live HTTP data pulls.
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/114.0.0.0 Safari/537.36",
            "Accept": "application/json, text/html, */*"
        })

    def set_api_key(self, api_key: str) -> None:
        """Set API key for authenticated endpoints."""
        self.api_key = api_key
        self.session.headers["Authorization"] = f"Bearer {api_key}"


def http_get(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 20,
) -> requests.Response:
    """
    Generic GET that always pulls live data from the URL.

    This is the core reusable function used by all government portal connectors.
    Every call hits the live endpoint - no caching, no static files.

    Args:
        url: Full URL of the government API endpoint
        params: Optional query parameters as a dict
        headers: Optional custom HTTP headers
        timeout: Request timeout in seconds (default: 20)

    Returns:
        requests.Response object from the live endpoint

    Raises:
        HttpError: If status code is not 200

    Example:
        >>> resp = http_get("https://data.gov.in/resource/abc123")
        >>> data = resp.json()
    """
    final_headers = headers or {}
    logger.info("GET %s params=%s", url, params)

    try:
        resp = requests.get(
            url,
            params=params,
            headers=final_headers,
            timeout=timeout
        )
    except requests.exceptions.Timeout as e:
        raise HttpError(f"GET {url} timed out after {timeout}s: {e}")
    except requests.exceptions.ConnectionError as e:
        raise HttpError(f"GET {url} connection failed: {e}")

    if resp.status_code != 200:
        body_snippet = resp.text[:200] if resp.text else "<empty response>"
        raise HttpError(
            f"GET {url} failed: {resp.status_code} {body_snippet}"
        )

    logger.info("GET %s returned status=%s", url, resp.status_code)
    return resp


def http_post(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 20,
) -> requests.Response:
    """
    Generic POST for government APIs that require form submissions.

    Args:
        url: Full URL of the government API endpoint
        data: Optional form data as a dict
        json_data: Optional JSON body as a dict
        headers: Optional custom HTTP headers
        timeout: Request timeout in seconds (default: 20)

    Returns:
        requests.Response object from the live endpoint

    Raises:
        HttpError: If status code is not 200
    """
    final_headers = headers or {}
    logger.info("POST %s data=%s", url, data or json_data)

    try:
        if json_data:
            resp = requests.post(
                url,
                json=json_data,
                headers=final_headers,
                timeout=timeout
            )
        else:
            resp = requests.post(
                url,
                data=data,
                headers=final_headers,
                timeout=timeout
            )
    except requests.exceptions.Timeout as e:
        raise HttpError(f"POST {url} timed out after {timeout}s: {e}")
    except requests.exceptions.ConnectionError as e:
        raise HttpError(f"POST {url} connection failed: {e}")

    if resp.status_code != 200:
        body_snippet = resp.text[:200] if resp.text else "<empty response>"
        raise HttpError(
            f"POST {url} failed: {resp.status_code} {body_snippet}"
        )

    logger.info("POST %s returned status=%s", url, resp.status_code)
    return resp
