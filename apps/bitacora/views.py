from django.shortcuts import render
from .models import AuditAdmin
from .api_client import BitacoraAPIClient
import logging
from django.http import JsonResponse
from .api_client import BitacoraAPIClient

logger = logging.getLogger(__name__)

def get_records(request):
    v = 15
    entity = request.GET.get("entity", "usuarios")

    resp = BitacoraAPIClient.list_records(request, entity, v)
    return JsonResponse(resp.get("response", []), safe=False)

def bitacora_view(request):
    v = 15  # versión de tus endpoints

    # ================= REGISTROS LOCALES =================
    registros = AuditAdmin.objects.order_by('-created_at')[:100]

    # ================= CONTEXTO =================
    context = {
        "registros": registros,

        # catálogos
        "modulos": [],
        "entidades": [],
        "acciones": [],
        "registros_catalogo": [],
    }

    try:
        # ================= MÓDULOS =================
        modules_resp = BitacoraAPIClient.list_modules(request, v)
        context["modulos"] = modules_resp.get("response", [])

        # ================= ENTIDADES =================
        entities_resp = BitacoraAPIClient._raw_get(
            request,
            "entities",
            {"v": v}
        )
        context["entidades"] = entities_resp.get("response", [])

        # ================= ACCIONES =================
        actions_resp = BitacoraAPIClient._raw_get(
            request,
            "actions",
            {"v": v}
        )
        context["acciones"] = actions_resp.get("response", [])

        # ================= REGISTROS (DEPENDE DE ENTIDAD) =================
        # si no seleccionan nada, usamos "usuarios" como default
        entidad = request.GET.get("entity", "usuarios")

        records_resp = BitacoraAPIClient._raw_get(
            request,
            "records",
            {"id": entidad, "v": v}
        )
        context["registros_catalogo"] = records_resp.get("response", [])

    except Exception as e:
        logger.exception("Error cargando catálogos de bitácora")

    return render(request, "bitacora.html", context)
