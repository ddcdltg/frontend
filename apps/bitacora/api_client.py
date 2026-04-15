from requests.exceptions import RequestException
from django.conf import settings
import logging
import requests
import time

log = logging.getLogger(__name__)


class CertificateManager:
    """
    CertificateManager de prueba:
    - Maneja sesión HTTP reutilizable
    - Timeout configurable
    - Cache simple por TTL (muy básico, solo para demo)
    """

    def __init__(self, cache_ttl=3600, timeout=5.0):
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.session = requests.Session()
        self._last_refresh = time.time()

    def _refresh_if_needed(self):
        """
        Simula refresco de certificados/token cada TTL
        """
        now = time.time()
        if now - self._last_refresh > self.cache_ttl:
            log.debug("Refrescando sesión/certificados (simulado)")
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
        """
        Wrapper sobre requests
        """
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
                verify=False  # ⚠️ solo para pruebas (SSL deshabilitado)
            )

            return resp

        except requests.RequestException as e:
            log.exception("Error en request hacia %s", url)
            raise e


# ================= INSTANCIA =================
cm = CertificateManager(cache_ttl=3600, timeout=5.0)
API_BASE_BACK_URL = "http://127.0.0.1:9002"
BASE = API_BASE_BACK_URL.rstrip("/") + "/data_bitacora"

# ================= HELPERS =================
def build_url(base, endpoint, params=None):
    from urllib.parse import urlencode

    url = f"{base}/{endpoint}"
    if params:
        return f"{url}?{urlencode(params)}"
    return url


def build_headers(request):
    headers = {
        "Content-Type": "application/json"
    }

    if request and hasattr(request, "META"):
        auth = request.META.get("HTTP_AUTHORIZATION")
        if auth:
            headers["Authorization"] = auth

    return headers


# ================= CLIENTE =================
class BitacoraAPIClient:
    """
    Cliente para consumir endpoints de bitácoras/auditoría desde el Resource Server.

    Convención esperada:
      - resp.json() devuelve: httpCode, message, response
      - list_dt devuelve formato DataTables
    """

    # ================= GENERICO =================
    @classmethod
    def _raw_get(cls, request, endpoint: str, params: dict):
        try:
            url = build_url(BASE, endpoint, params)

            resp = cm.request(
                "GET",
                url,
                headers=build_headers(request),
                follow_redirects=True,
                timeout=10.0,
            )

            return resp.json()

        except RequestException as e:
            if getattr(e, "response", None) is not None:
                try:
                    return e.response.json()
                except Exception:
                    log.exception("Error no-json en %s", endpoint)

            return {"success": False, "response": []}

    # ================= DATA TABLE =================
    @classmethod
    def list_dt(cls, view_id: int, dt_params: dict, request=None):
        try:
            url = build_url(BASE, "audit", {"v": view_id})

            logging.debug(
                "BitacoraAPIClient.list_dt request to %s with params: %s",
                url,
                dt_params
            )

            resp = cm.request(
                "POST",
                url,
                headers=build_headers(request),
                json=dt_params,
                follow_redirects=True,
                timeout=10.0,
            )

            logging.debug(
                "BitacoraAPIClient.list_dt response: %s",
                resp.text[:500]
            )

            return resp.json()

        except RequestException as e:
            if getattr(e, "response", None) is not None:
                try:
                    return e.response.json()
                except Exception:
                    log.exception(
                        "RS no-json body: %s",
                        getattr(e.response, "text", "")[:500]
                    )

            return {
                "httpCode": 502,
                "error": "bad_gateway",
                "message": "No se pudo contactar el servicio",
                "response": {
                    "draw": dt_params.get("draw", 1),
                    "recordsTotal": 0,
                    "recordsFiltered": 0,
                    "data": [],
                },
            }

    # ================= DETALLE =================
    @classmethod
    def get_detail(cls, audit_id: int, request, v: int):
        try:
            url = build_url(BASE, "audit_detail", {"id": audit_id, "v": v})

            resp = cm.request(
                "GET",
                url,
                headers=build_headers(request),
                follow_redirects=True,
                timeout=10.0,
            )

            resp.raise_for_status()
            return resp.json()

        except RequestException as e:
            if getattr(e, "response", None) is not None:
                try:
                    return e.response.json()
                except Exception:
                    pass
            return {}

    # ================= MODULOS =================
    @classmethod
    def list_modules(cls, request, v: int):
        try:
            url = build_url(BASE, "audit_modules", {"v": v})

            resp = cm.request(
                "GET",
                url,
                headers=build_headers(request),
                follow_redirects=True,
                timeout=10.0,
            )

            return resp.json()

        except RequestException:
            return {"success": False, "response": []}

    # ================= ENTIDADES =================
    @classmethod
    def list_entities(cls, request, v: int):
        return cls._raw_get(request, "entities", {"v": v})

    # ================= ACCIONES =================
    @classmethod
    def list_actions(cls, request, v: int):
        return cls._raw_get(request, "actions", {"v": v})

    # ================= REGISTROS =================
    @classmethod
    def list_records(cls, request, entity: str, v: int):
        return cls._raw_get(
            request,
            "records",
            {"id": entity, "v": v}
        )

    # ================= EVENTO =================
    @classmethod
    def get_event(cls, request, event_id: str, v: int):
        return cls._raw_get(
            request,
            "audit/event",
            {"event_id": event_id, "v": v}
        )