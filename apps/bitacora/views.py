from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json

from .models import AuditAdmin
from .api_client import BitacoraAPIClient

logger = logging.getLogger("name")


# ================= RECORDS POR ENTIDAD =================
def get_records(request):
    v = 15
    entity = request.GET.get("entity", "usuarios")

    resp = BitacoraAPIClient.list_records(request, entity, v)

    return JsonResponse(resp.get("response", []), safe=False)


# ================= VISTA PRINCIPAL =================
def bitacora_view(request):
    v = 15

    context = {
        "modulos": [],
        "entidades": [],
        "acciones": [],
        "registros_catalogo": [],
    }

    try:
        # ENTIDADES
        entities_resp = BitacoraAPIClient.list_entities(request, v)
        context["entidades"] = entities_resp.get("response", [])

        # ACCIONES
        actions_resp = BitacoraAPIClient.list_actions(request, v)
        context["acciones"] = actions_resp.get("response", [])

        # RECORDS DEFAULT
        entidad = request.GET.get("entity", "usuarios")

        records_resp = BitacoraAPIClient.list_records(
            request,
            entidad,
            v
        )
        context["registros_catalogo"] = records_resp.get("response", [])

    except Exception:
        logger.exception("Error cargando catálogos de bitácora")

    return render(request, "bitacora.html", context)


# ================= DATATABLE SERVER-SIDE =================
@csrf_exempt
def bitacora_data(request):

    if request.method != "POST":
        return JsonResponse({
            "draw": 1,
            "recordsTotal": 0,
            "recordsFiltered": 0,
            "data": []
        })

    try:
        body = json.loads(request.body)

        # ===== PARAMS BASE =====
        draw = body.get("draw", 1)
        start = body.get("start", 0)
        length = body.get("length", 10)

        # ===== PARSE COLUMNS =====
        columns = []
        i = 0
        while True:
            col = body.get(f"columns[{i}][data]")
            if col is None:
                break
            columns.append(col)
            i += 1

        # ===== PARSE ORDER =====
        order_column = body.get("order[0][column]")
        order_dir = body.get("order[0][dir]")

        order_by = None
        if order_column is not None and columns:
            try:
                col_name = columns[int(order_column)]
                order_by = f"-{col_name}" if order_dir == "desc" else col_name
            except Exception:
                logger.warning("Error parsing order column")

        # ===== FILTROS =====
        filters = {}

        entity = body.get("entity")
        action = body.get("action")
        record = body.get("record")
        date_from = body.get("date_from")
        date_to = body.get("date_to")

        if entity:
            filters["table_name"] = entity

        if action:
            filters["action"] = action

        if record:
            filters["record_id"] = record

        if date_from:
            filters["date_from"] = date_from

        if date_to:
            filters["date_to"] = date_to

        # ===== PARAMS PARA API =====
        dt_params = {
            "draw": draw,
            "start": start,
            "length": length,
        }

        if order_by:
            dt_params["order_by"] = order_by

        if filters:
            dt_params["filters"] = filters

        # ===== LLAMADA AL BACK =====
        resp = BitacoraAPIClient.list_dt(
            15,
            dt_params,
            request
        )

        data = resp.get("response", {})

        # ===== RESPUESTA A DATATABLE =====
        return JsonResponse({
            "draw": data.get("draw", draw),
            "recordsTotal": data.get("recordsTotal", 0),
            "recordsFiltered": data.get("recordsFiltered", 0),
            "data": data.get("data", [])
        })

    except Exception:
        logger.exception("Error en DataTable de bitácora")

        return JsonResponse({
            "draw": 1,
            "recordsTotal": 0,
            "recordsFiltered": 0,
            "data": []
        })