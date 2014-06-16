import autocomplete_light
from repocasos.models import *
from snomedct.models import sct_description

autocomplete_light.register(sct_description,
    search_fields=['term'],
    choices=sct_description.objects.filter(descriptiontype__exact=0),
    attrs={
        'placeholder': 'SNOMED-CT (BETA)',
        'data-widget-minimum-characters': 1,
        })

__author__ = 'ehebel'
