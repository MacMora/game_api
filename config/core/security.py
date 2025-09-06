# core/security.py
from rest_framework.throttling import SimpleRateThrottle

class IPBurstThrottle(SimpleRateThrottle):
    scope = "ip_burst"
    def get_cache_key(self, request, view):
        ident = self.get_ident(request)  # IP
        return self.cache_format % {"scope": self.scope, "ident": ident}

class IPSustainedThrottle(SimpleRateThrottle):
    scope = "ip_sustained"
    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}
