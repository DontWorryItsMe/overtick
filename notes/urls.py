# C:\Users\Admin\overtick\notes\urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('folder/<int:pk>/', views.folder_detail, name='folder_detail'),
    path('note/<int:pk>/', views.note_detail, name='note_detail'),
    path('tag/<int:pk>/', views.tag_detail, name='tag_detail'),
    path('search/', views.search, name='search'),
    path('upload/', views.upload_file, name='upload_file'),
    path('create_note/', views.create_note, name='create_note'),
    path('create_folder/', views.create_folder, name='create_folder'),
    path('export/', views.export_notes, name='export_notes'),
    path('note/<int:note_id>/export/', views.export_note, name='export_note'),
    path('download/<int:pk>/', views.download_file, name='download_file'),
    path('media/<path:path>/', views.serve_media, name='serve_media'),
    path('view_file/<int:file_id>/', views.view_file, name='view_file'),
    path('view_note/<int:note_id>/', views.view_note, name='view_note'),
    path('view_folder/<int:folder_id>/', views.view_folder, name='view_folder'),
    path('edit_file/<int:file_id>/', views.edit_file, name='edit_file'),
    path('edit_note/<int:note_id>/', views.edit_note, name='edit_note'),
    path('folder/<int:folder_id>/edit/', views.edit_folder, name='edit_folder'),
    path('delete_file/<int:file_id>/', views.delete_file, name='delete_file'),
    path('delete_note/<int:note_id>/', views.delete_note, name='delete_note'),
    path('delete_folder/<int:folder_id>/', views.delete_folder, name='delete_folder'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
