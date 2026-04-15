from django.urls import path
from .views import bitacora_view, get_records

urlpatterns = [
    path("bitacora/", bitacora_view, name="bitacora"),
    path("get-records/", get_records, name="get_records")
]