# Connectors package for India Anti-Corruption Project
# Live data connectors for Indian government portals

from .base import http_get, HttpError

__all__ = ["http_get", "HttpError"]
