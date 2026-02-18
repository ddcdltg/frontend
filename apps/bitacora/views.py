from django.shortcuts import render

from django.http import HttpResponse

def hola_mundo(request):
    return HttpResponse("¡Hola Mundo desde Django!")
