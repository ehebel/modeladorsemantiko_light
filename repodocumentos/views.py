from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import FormView,DetailView,ListView

from repodocumentos.forms import ArchivosSubidosForm
from repodocumentos.models import ArchivoSubido

class ArchivosSubidosView(FormView):
    template_name = 'docrepo/subir_archivo_form.html'
    form_class = ArchivosSubidosForm

    def form_valid(self, form):
        archivo_subido = ArchivoSubido(
            archivo = self.get_form_kwargs().get('files')['archivo'])
        archivo_subido.save()
        self.id = archivo_subido.id


        return  HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('archivo_lista')

class ArchivoDetalleVista(DetailView):
    model = ArchivoSubido
    template_name = 'docrepo/archivos_subidos_lista.html'
    context_object_name = 'archivo'



class ArchivoIndiceVista(ListView):
    model = ArchivoSubido
    template_name = 'docrepo/archivos_subidos_lista.html'
    context_object_name = 'archivos'
    queryset = ArchivoSubido.objects.all()
