#!/usr/bin/env python3
from django.http import HttpResponseForbidden
from django.core.cache import cache
from ipware import get_client_ip
from ip_tracking.models import RequestLog, BlockedIP
from ipgeolocation import IpGeolocationAPI

# Initialize the API client
api_key = 'your_api_key_here'  # 🔐 Replace with your real API key
geo_api = IpGeolocationAPI(api_key)


class IPTrackingMiddleware:
    """Middleware to log and block IPs, and enrich logs with geolocation."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip, _ = get_client_ip(request)
        if ip:
            # Block IP if blacklisted
            if BlockedIP.objects.filter(ip_address=ip).exists():
                return HttpResponseForbidden("Access denied.")

            # Get geolocation from cache or API
            cache_key = f"geo:{ip}"
            geo_data = cache.get(cache_key)
            if not geo_data:
                response = geo_api.get_geolocation_data(ip)
                geo_data = {
                    "country": response.get("country_name", ""),
                    "city": response.get("city", "")
                }
                cache.set(cache_key, geo_data, 86400)  # 24 hours cache

            RequestLog.objects.create(
                ip_address=ip,
                path=request.path,
                country=geo_data["country"],
                city=geo_data["city"]
            )

        return self.get_response(request)

