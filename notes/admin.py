# C:\Users\Admin\overtick\notes\admin.py

from django.contrib import admin
from .models import Note, Folder, UploadedFile

admin.site.register(Note)
admin.site.register(Folder)
admin.site.register(UploadedFile)


