from requests.exceptions import RequestException
import requests
import logging
import time
from django.conf import settings

log = logging.getLogger(__name__)


# CERTIFICATE MANAGER

class CertificateManager:

    def __init__(self, cache_ttl=3600, timeout=5.0):
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.session = requests.Session()
        self._last_refresh = time.time()

    def _refresh_if_needed(self):
        now = time.time()
        if now - self._last_refresh > self.cache_ttl:
            log.debug("Refrescando sesión HTTP")
            self.session = requests.Session()
            self._last_refresh = now

    def request(
        self,
        method,
        url,
        headers=None,
        json=None,
        params=None,
        follow_redirects=True,
        timeout=None,
    ):
        self._refresh_if_needed()

        try:
            resp = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                params=params,
                allow_redirects=follow_redirects,
                timeout=timeout or self.timeout,
                verify=False
            )

            resp.raise_for_status()
            return resp

        except requests.RequestException as e:
            log.exception("Error HTTP hacia %s", url)
            raise e



# CONFIG

cm = CertificateManager(cache_ttl=3600, timeout=10.0)

API_BASE_BACK_URL = getattr(
    settings,
    "API_BASE_BACK_URL",
    "http://127.0.0.1:9002"
)

BASE = API_BASE_BACK_URL.rstrip("/") + "/data_bitacora"



# HELPERS

def build_url(base, endpoint, params=None):
    from urllib.parse import urlencode

    url = f"{base}/{endpoint}"
    if params:
        return f"{url}?{urlencode(params)}"
    return url


def build_headers(request):
    return {
        "Content-Type": "application/json",
        "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJuYW1lIjoiVXN1YXJpbyBQcnVlYmEiLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE3MTAwMDAwMDB9.dGVzdF9zaWduYXR1cmFfbm9fdmFsaWRh"
    }


# CLIENTE BITÁCORA

class BitacoraAPIClient:

    @classmethod
    def _raw_get(cls, request, endpoint: str, params: dict):
        try:
            url = build_url(BASE, endpoint, params)

            resp = cm.request(
                "GET",
                url,
                headers=build_headers(request),
                timeout=10.0,
            )

            return resp.json()

        except RequestException:
            log.error("GET error en %s", endpoint)
            return {
                "httpCode": 500,
                "message": "Error en GET",
                "response": []
            }

    @classmethod
    def list_dt(cls, view_id: int, dt_params: dict, request=None):
        try:
            url = build_url(BASE, "audit", {"v": view_id})

            log.debug("POST DataTable → %s", url)
            log.debug("Payload → %s", dt_params)

            resp = cm.request(
                "POST",
                url,
                headers=build_headers(request),
                json=dt_params,
                timeout=10.0,
            )

            return resp.json()

        except RequestException:
            log.error("Error en DataTable audit")
            return {
                "httpCode": 502,
                "message": "Error backend",
                "response": {
                    "draw": dt_params.get("draw", 1),
                    "recordsTotal": 0,
                    "recordsFiltered": 0,
                    "data": []
                }
            }

    @classmethod
    def list_entities(cls, request, v: int):
        return cls._raw_get(request, "entities", {"v": v})

    @classmethod
    def list_actions(cls, request, v: int):
        return cls._raw_get(request, "actions", {"v": v})

    @classmethod
    def list_records(cls, request, entity: str, v: int):
        return cls._raw_get(
            request,
            "records",
            {"id": entity, "v": v}
        )

    @classmethod
    def list_modules(cls, request, v: int):
        return cls._raw_get(request, "audit_modules", {"v": v})

    @classmethod
    def get_detail(cls, audit_id: int, request, v: int):
        return cls._raw_get(
            request,
            "audit_detail",
            {"id": audit_id, "v": v}
        )

    @classmethod
    def get_event(cls, request, event_id: str, v: int):
        return cls._raw_get(
            request,
            "audit/event",
            {"event_id": event_id, "v": v}
        )