import autocomplete_light
from efectorescas.models import *

autocomplete_light.register(efector,
    search_fields=['ExamCode','ExamName'],
    attrs={
        'placeholder': 'Efector',
        'data-widget-minimum-characters': 1,
        })

autocomplete_light.register(conceptosCASporarea,
    search_fields=['concepto__fsn'],
    attrs={
        'placeholder': 'Concepto-Area',
        'data-widget-minimum-characters': 1,
        })


autocomplete_light.register(concepto,
    search_fields=['fsn',],
    attrs={
        'placeholder': 'descripcion',
        'data-widget-minimum-characters': 1,
        })

autocomplete_light.register(cas_area,
    search_fields=['descripcion',],
    attrs={
        'placeholder': 'areas',
        'data-widget-minimum-characters': 1,
        })


__author__ = 'ehebel'
