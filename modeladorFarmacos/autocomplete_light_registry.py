import autocomplete_light
from modeladorFarmacos.models import *

autocomplete_light.register(xt_mb,
    search_fields=['descripcion'],
    attrs={
        'placeholder': 'ej. IBUPROFENO + PARACETAMOL',
        'data-widget-minimum-characters': 1,
        })

autocomplete_light.register(xt_mb, search_fields=('descripcion',),
    attrs={'placeholder': 'ej. IBUPROFENO + PARACETAMOL '})

autocomplete_light.register(registroSanitario, search_fields=('nombre','registro'),
    attrs={'placeholder': 'Registro ISPCH'})

autocomplete_light.register(xt_unidad_dosis_unitaria, search_fields=('descripcion',),
    attrs={'placeholder': 'ej. ampolla, comprimido..'})

autocomplete_light.register(xt_unidad_medida_unitaria, search_fields=('descripcion',),
    attrs={'placeholder': 'ej. comprimido'})

autocomplete_light.register(xt_forma_farm, search_fields=('descripcion',),
    attrs={'placeholder': 'ej. comprimido efervescente '})


autocomplete_light.register(xt_sustancia, search_fields=('descripcion',),
    choices=xt_sustancia.objects.filter(estado=False),
    attrs={'placeholder': 'ej. paracetamol'})


autocomplete_light.register(xt_mc, search_fields=('descripcion',),
    attrs={'placeholder': 'ej. PARACETAMOL 500 MG COMPRIMIDO'})

autocomplete_light.register(xt_mcce, search_fields=('descripcion',),
    attrs={'placeholder': 'Inserte aqui'})


autocomplete_light.register(rel_xt_mb_xt_sust, search_fields=('descripcion',),
    attrs={'placeholder': 'Rel Medicamentos Clinicos .. '})

autocomplete_light.register(rel_mc_sust, search_fields=('descripcion',),
    attrs={'placeholder': 'Rel Medicamentos Clinicos .. '})


autocomplete_light.register(xt_pc, search_fields=('descripcion',),
    attrs={'placeholder': 'ej. TAREG 160 MG COMPRIMIDOS RECUBIERTOS (NOVARTIS)'})


autocomplete_light.register(kairos_presentaciones, search_fields=('claveproducto__descripcion','claveproducto__clave'),
    choices=kairos_presentaciones.objects.exclude(estado__icontains='B'),
    attrs={'placeholder': 'ej. Ginotex'})

autocomplete_light.register(xt_fp, search_fields=('descripcion',),
    attrs={'placeholder': 'ej. Panadol...'})


autocomplete_light.register(atc, search_fields=('atc_desc','cod_atc'),
    attrs={'placeholder': 'Codigo o Desc ATC'})

autocomplete_light.register(kairos_productos, search_fields=('descripcion',),)

autocomplete_light.register(dbnet, search_fields=('producto',),)

autocomplete_light.register(xt_laboratorio, search_fields=('desc_abrev','descripcion'),
    attrs={'placeholder': 'Laboratorio'}
)

__author__ = 'ehebel'
