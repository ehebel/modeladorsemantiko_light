import autocomplete_light
from efectorescas.models import *

autocomplete_light.register(efector,
    search_fields=['ExamCode','ExamName'],
    attrs={
        'placeholder': 'Efector',
        'data-widget-minimum-characters': 1,
        })

#autocomplete_light.register(conceptosCASporarea,
#    search_fields=['concepto'],
#    attrs={
#        'placeholder': 'Concepto-Area',
#        'data-widget-minimum-characters': 1,
#        })

__author__ = 'ehebel'
