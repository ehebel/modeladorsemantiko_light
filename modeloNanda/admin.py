import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
from modeloNanda.models import *

admin.autodiscover()

from django.db.models import get_models, get_app
from django.contrib.admin.sites import AlreadyRegistered

def autoregister(*app_list):
    for app_name in app_list:
        app_models = get_app(app_name)
        for model in get_models(app_models):
            try:
                admin.site.register(model)
            except AlreadyRegistered:
                pass


autoregister('modeloNic', 'modeloNoc',)

class nandaClaseAdmin(admin.ModelAdmin):
    # This will generate a ModelForm
    form = autocomplete_light.modelform_factory(nandaClase)

admin.site.register(nandaClase,nandaClaseAdmin)

admin.site.register(nanda)
admin.site.register(nandaDominio)
admin.site.register(nandaValoracion)
admin.site.register(nandaTipo)
admin.site.register(nandaCaracteristica)


__author__ = 'ehebel'
