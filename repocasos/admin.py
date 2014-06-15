import autocomplete_light
autocomplete_light.autodiscover()
from django.contrib import admin
admin.autodiscover()
from repocasos.models import *

class casoAdmin(admin.ModelAdmin):

    form = autocomplete_light.modelform_factory(caso)

admin.site.register(caso,casoAdmin)


__author__ = 'ehebel'
