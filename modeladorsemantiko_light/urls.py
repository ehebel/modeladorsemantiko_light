from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:

from django.views import generic

import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
admin.autodiscover()

from modeloNanda.api import EntryResource, UserResource
from tastypie.api import Api

from modeladorFarmacos.views import *

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(EntryResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'modeladorsemantiko_light.views.home', name='home'),
    # url(r'^modeladorsemantiko_light/', include('modeladorsemantiko_light.foo.urls')),
    url(r'^modelador_light/autocomplete/', include('autocomplete_light.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^modelador_light/admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^modelador_light/admin/', include(admin.site.urls)),

    (r'^modelador_light/api/', include(v1_api.urls)),
    (r'^modelador_light/favicon.ico', generic.RedirectView.as_view(url='http://mozilla.org/favicon.ico')),

    (r'^modelador_light/$', generic.TemplateView.as_view(template_name='index.html')),


#    (r'^modelador/catalogo/$', lista_mc),
    (r'^modelador_light/pendientes/$', pendientes),


    (r'^modelador_light/kairos_capsulas/$', kairos2),

    (r'^modelador_light/kairos/$', kairos_global),
    (r'^modelador_light/kairos_tabletas/$', kairos_tabletas),
    (r'^modelador_light/kairos_gotas/$', kairos_gotas),
    (r'^modelador_light/kairos_jarabes/$', kairos_jarabes),
    (r'^modelador_light/kairos_ampollas/$', kairos_ampollas),
    (r'^modelador_light/kairos_colirios/$', kairos_colirios),
    (r'^modelador_light/kairos_cremas/$', kairos_cremas),
    (r'^modelador_light/kairos_parches/$', kairos_parches),
    (r'^modelador_light/kairos_shampoo/$', kairos_shampoo),
    (r'^modelador_light/kairos_supositorios/$', kairos_supositorios),

)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()