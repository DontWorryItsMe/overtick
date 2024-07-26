# C:\Users\Admin\overtick\overthink\urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('notes.urls')),  # Includes the URLs from the notes app
]