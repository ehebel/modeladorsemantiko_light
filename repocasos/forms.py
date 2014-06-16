import datetime
import autocomplete_light
autocomplete_light.autodiscover()
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ValidationError
from django.contrib.admin import widgets
from django.forms import Textarea, TextInput

from repocasos.models import caso


class CasoForm(autocomplete_light.ModelForm):
#class CasoForm(forms.Form):
#    tagging = autocomplete_light.MultipleChoiceWidget('radlexAutocomplete')
#    fechacaso = DateField(widget = AdminDateWidget)
    class Meta:

        model = caso
        widgets = {
            'observacion': Textarea(attrs={'cols':40, 'rows':5}),
#            'fechacaso': SelectDateWidget,
            'url': TextInput(attrs={'size':'100'}),
            }
    def __init__(self, *args, **kwargs):
        super(CasoForm, self).__init__(*args, **kwargs)
        self.fields['fechacaso'].widget = widgets.AdminDateWidget()

__author__ = 'ehebel'

