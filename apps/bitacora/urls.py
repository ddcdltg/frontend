from django.urls import path
from .views import (
BitacoraEventDetailData,
bitacora_view,
get_records,
bitacora_data
)

urlpatterns = [
# Vista principal
path("bitacora/", bitacora_view, name="bitacora"),

# AJAX: obtener records por entidad
path("get-records/", get_records, name="get_records"),

# DataTables server-side (filtros + paginación)
path("data/", bitacora_data, name="bitacora_data"),

path("event-detail/<str:event_id>/", BitacoraEventDetailData.as_view(), name="event_detail"),

]
