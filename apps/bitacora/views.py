from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json

from .models import AuditAdmin
from .api_client import BitacoraAPIClient

logger = logging.getLogger("name")

# RECORDS POR ENTIDAD (AJAX)

def get_records(request):
    v = 15
    entity = request.GET.get("entity", "usuarios")


    resp = BitacoraAPIClient.list_records(request, entity, v)

    # devolvemos solo el array limpio
    return JsonResponse(resp.get("response", []), safe=False)

# VISTA PRINCIPAL

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

        # RECORDS (DEFAULT: usuarios)
        entidad = request.GET.get("entity", "usuarios")

        records_resp = BitacoraAPIClient.list_records(
            request,
            entidad,
            v,
        )
        context["registros_catalogo"] = []

    except Exception:
        logger.exception("Error cargando catálogos de bitácora")

    return render(request, "bitacora.html", context)

# DATATABLE SERVER-SIDE
"""
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

            # PARAMS BASE DATATABLE
            dt_params = {
                "draw": body.get("draw", 1),
                "start": body.get("start", 0),
                "length": body.get("length", 10),
                "order": body.get("order", [0]),
                "columns": body.get("columns", []),
            }

            # FILTROS
            filters = {}

            f = body.get("filters", {})

            entity = f.get("table_name")
            action = f.get("action")
            record = f.get("record_id")
            date_from = f.get("date_from")
            date_to = f.get("date_to")

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

            if filters:
                dt_params["filters"] = filters

            # LLAMADA AL BACK 
            resp = BitacoraAPIClient.list_dt(
                15,
                dt_params,
                request
            )

            data = resp.get("response", {})

            return JsonResponse({
                "draw": data.get("draw", 1),
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
    
"""

import json
from django.http import JsonResponse
from django.db.models import Q

def bitacora_data(request):
    try:
        data = json.loads(request.body)

        draw = data.get('draw', 1)
        start = data.get('start', 0)
        length = data.get('length', 10)

        search_value = data.get('search', '')  # 🔥 AQUÍ

        filters = data.get('filters', {})

        table_name = filters.get('table_name')
        action = filters.get('action')
        record_id = filters.get('record_id')
        date_from = filters.get('date_from')
        date_to = filters.get('date_to')

        queryset = AuditAdmin.objects.all()

        # ================= FILTROS =================
        if table_name:
            queryset = queryset.filter(table_name=table_name)

        if action:
            queryset = queryset.filter(action=action)

        if record_id:
            queryset = queryset.filter(record_id=record_id)

        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        # ================= SEARCH GLOBAL =================
        if search_value:
            queryset = queryset.filter(
                Q(event_id__icontains=search_value) |
                Q(action__icontains=search_value) |
                Q(table_name__icontains=search_value) |
                Q(record_id__icontains=search_value) |
                Q(field_name__icontains=search_value) |
                Q(value__icontains=search_value)
            )

        total_records = queryset.count()

        # ================= PAGINACIÓN =================
        queryset = queryset.order_by('audit_id')[start:start+length]

        data_result = list(queryset.values(
            "audit_id",
            "event_id",
            "created_at",
            "actor_id",
            "view_id",
            "ip_address",
            "action",
            "table_name",
            "record_id",
            "field_name",
            "value",
            "meta"
        ))

        return JsonResponse({
            "draw": draw,
            "recordsTotal": total_records,
            "recordsFiltered": total_records,
            "data": data_result
        })

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=500)