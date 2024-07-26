# C:\Users\Admin\overtick\notes\views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponse, Http404
from .models import Note, Folder, UploadedFile
from django.template.loader import render_to_string, get_template
from django.db.models import Q
import markdown2
from taggit.models import Tag
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_protect
from django.http import FileResponse
from .forms import NoteForm, FolderForm, UploadedFileForm
import os

def index(request):
    if not request.session.get('authenticated', False):
        return redirect('login')
    folders = Folder.objects.filter(parent__isnull=True)
    notes = Note.objects.filter(folder__isnull=True)
    uploaded_files = UploadedFile.objects.all()
    context = {
        'folders': folders,
        'notes': notes,
        'uploaded_files': uploaded_files,
        'index_url': reverse('index'),
        'search_url': reverse('search'),
    }
    return render(request, 'notes/index.html', context)

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == settings.APP_PASSWORD:
            request.session['authenticated'] = True
            request.session.set_expiry(0)  # Session expires when browser closes
            return redirect('index')
        else:
            return render(request, 'notes/login.html', {'error_message': 'Incorrect password. Please try again.'})
    return render(request, 'notes/login.html')

def notify_group(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "sync_group",
        {
            "type": "sync.message",
            "message": message,
        },
    )

# Example usage in a view
def create_note(request):
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            notify_group("A new note was created")
            return redirect('index')
    else:
        form = NoteForm()
    return render(request, 'notes/create_note.html', {'form': form})

def folder_detail(request, pk):
    folder = get_object_or_404(Folder, pk=pk)
    subfolders = Folder.objects.filter(parent=folder)
    notes = Note.objects.filter(folder=folder)
    return render(request, 'notes/folder_detail.html', {'folder': folder, 'subfolders': subfolders, 'notes': notes})

def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk)
    content_html = markdown2.markdown(note.content)
    return render(request, 'note_detail.html', {'note': note, 'content_html': content_html})

def tag_detail(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    notes = Note.objects.filter(tags=tag)
    return render(request, 'notes/tag_detail.html', {'tag': tag, 'notes': notes})

def search(request):
    query = request.GET.get('query', '')
    note_results = Note.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
    folder_results = Folder.objects.filter(Q(name__icontains=query))
    file_results = UploadedFile.objects.filter(Q(description__icontains=query) | Q(file__icontains=query))
    results = list(note_results) + list(folder_results) + list(file_results)
    context = {'results': results, 'query': query}
    return render(request, 'notes/search_results.html', context)

def upload_file(request):
    if request.method == 'POST':
        files = request.FILES.getlist('documents')
        for file in files:
            if file.size <= settings.MAX_FILE_SIZE:
                file_instance = UploadedFile(file=file)
                file_instance.save()
            else:
                return render(request, 'notes/upload.html', {'error': 'Invalid file size'})
        return redirect('index')
    return render(request, 'notes/upload.html')

def export_notes(request):
    notes = Note.objects.all()
    template_path = 'notes/export.html'
    context = {'notes': notes}
    html_string = render_to_string(template_path, context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode('UTF-8')), result)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="notes.pdf"'
        return response
    return HttpResponse('We had some errors <pre>' + html_string + '</pre>')

def export_note(request, note_id):
    note = Note.objects.get(id=note_id)
    template_path = 'notes/export_note.html'
    context = {'note': note}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="note_{}.pdf"'.format(note_id)
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def download_file(request, pk):
    file = get_object_or_404(UploadedFile, pk=pk)
    file_path = file.file.path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def serve_media(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    return FileResponse(open(file_path, 'rb'))

def view_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)
    return render(request, 'notes/view_file.html', {'file': file})

def view_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    return render(request, 'notes/view_note.html', {'note': note})

def view_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    notes = folder.notes.all()
    return render(request, 'notes/view_folder.html', {'folder': folder, 'notes': notes})

def edit_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)
    if request.method == "POST":
        form = UploadedFileForm(request.POST, request.FILES, instance=file)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = UploadedFileForm(instance=file)
    return render(request, 'notes/edit_file.html', {'form': form, 'file': file})

def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('note_detail', pk=note.id)
    else:
        form = NoteForm(instance=note)
    return render(request, 'notes/edit_note.html', {'form': form, 'note': note})

def edit_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    if request.method == 'POST':
        folder.name = request.POST.get('name')
        parent_id = request.POST.get('parent')
        if parent_id:
            folder.parent = get_object_or_404(Folder, id=parent_id)
        folder.save()
        return redirect('folder_detail', pk=folder.id)
    else:
        folders = Folder.objects.exclude(id=folder.id)
        return render(request, 'notes/edit_folder.html', {'folder': folder, 'folders': folders})

def delete_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)
    if request.method == "POST":
        file.delete()
        return redirect('index')
    return render(request, 'notes/delete_file.html', {'file': file})

def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    if request.method == "POST":
        note.delete()
        return redirect('index')
    return render(request, 'notes/delete_note.html', {'note': note})

def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    if request.method == "POST":
        folder.delete()
        return redirect('index')
    return render(request, 'notes/delete_folder.html', {'folder': folder})

def create_note(request):
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = NoteForm()
    return render(request, 'notes/create_note.html', {'form': form})

def create_folder(request):
    if request.method == "POST":
        form = FolderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = FolderForm()
    return render(request, 'notes/create_folder.html', {'form': form})


