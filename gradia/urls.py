from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('gizli-x9k2m/', admin.site.urls),
    path('', lambda request: redirect('survey'), name='root'),
    path('', include('core.urls')),
]
