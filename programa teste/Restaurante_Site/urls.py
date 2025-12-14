# Restaurante_Site/urls.py (CORREÇÃO FINAL)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # GARANTA QUE O APP 'cardapio' ESTEJA MISTURADO AQUI
    # O path DEVE SER APENAS '' (VAZIO) para que o menu seja /menu/
    path('', include('cardapio.urls')), 
]