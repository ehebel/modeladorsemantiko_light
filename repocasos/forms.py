import datetime
import autocomplete_light
autocomplete_light.autodiscover()
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ValidationError
from django.forms import Textarea, TextInput

from repocasos.models import caso


class CasoForm(autocomplete_light.ModelForm):
#class CasoForm(forms.Form):
#    tagging = autocomplete_light.MultipleChoiceWidget('radlexAutocomplete')
#    fechacaso = DateField(widget = AdminDateWidget)
    class Meta:

        model = caso
#        fields = ('fechacaso','nombre','appaterno','apmaterno','institucion','observacion')
        widgets = {
            'observacion': Textarea(attrs={'cols':40, 'rows':5}),
            'fechacaso': AdminDateWidget,
            'url': TextInput(attrs={'size':'100'}),
            }


__author__ = 'ehebel'
