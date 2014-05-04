from django import forms

class ArchivosSubidosForm(forms.Form):
    archivo = forms.FileField(label="Seleccione un archivo")

__author__ = 'ehebel'
