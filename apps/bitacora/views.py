from django.shortcuts import render

from django.http import HttpResponse

def hola_mundo(request):
    return HttpResponse("¡Hola Mundo desde Django!")

def indexbit(request):
    # Puedes pasar datos a la plantilla con un diccionario
    contexto = {
        'titulo': 'Mi primera página en Django',
        'mensaje': '¡Hola desde Django!'
    }
    return render(request, 'indexbit.html', contexto)
