from django.urls import path
from .views import bitacora_view, get_records, bitacora_data

urlpatterns = [
    path("", bitacora_view, name="bitacora"),
    path("get-records/", get_records, name="get_records"),
    path("data/", bitacora_data, name="bitacora_data"),
]