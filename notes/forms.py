# C:\Users\Admin\overtick\notes\forms.py

from django import forms
from .models import Note, Folder, UploadedFile
from taggit.forms import TagWidget

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'folder', 'tags']
        widgets = {
            'tags': TagWidget(attrs={'class': 'form-control'}),
        }

    tags = forms.CharField(required=False)

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent']

class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file', 'description']

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'folder', 'tags']
        widgets = {
            'tags': TagWidget(),
        }