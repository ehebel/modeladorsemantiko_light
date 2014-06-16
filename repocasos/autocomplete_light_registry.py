import autocomplete_light
from snomedct.models import sct_description

autocomplete_light.register(sct_description,
    search_fields=['term'],
    choices=sct_description.objects.filter(descriptionstatus__exact=0),
    attrs={
        'placeholder': 'SNOMED-CT (BETA)',
        'data-widget-minimum-characters': 1,
        })

__author__ = 'ehebel'
