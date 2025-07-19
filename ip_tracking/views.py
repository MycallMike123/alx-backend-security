#!/usr/bin/env python3
from django.http import JsonResponse
from ratelimit.decorators import ratelimit


@ratelimit(key='user', rate='10/m', method='POST', block=True)
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def login_view(request):
    """A sample login view protected by rate limiting."""
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return JsonResponse({'error': 'Rate limit exceeded.'}, status=429)

    return JsonResponse({'message': 'Login successful or placeholder.'})

