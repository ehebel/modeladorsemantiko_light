from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
# Uncomment the next two lines to enable the admin:

from django.views import generic
import autocomplete_light
from efectorescas.views import efectoresVistaImagenes, search
from modeladorFarmacos.forms import bioeqForm


autocomplete_light.autodiscover()

from django.contrib import admin
admin.autodiscover()

from modeloNanda.api import EntryResource, UserResource
from tastypie.api import Api

from modeladorFarmacos.views import *
import modeladorFarmacos.views

from repodocumentos.views import ArchivoDetalleVista,ArchivosSubidosView,ArchivoIndiceVista
from repocasos.views import ListCaseView,CreateCaseView, UpdateCaseView,DeleteCaseView,CaseView


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

    url(r'^modelador_light/login/$', 'django.contrib.auth.views.login'),
    url(r'^modelador_light/logout/$', 'django.contrib.auth.views.logout'),

    # Uncomment the next line to enable the admin:
    url(r'^modelador_light/admin/', include(admin.site.urls)),

    (r'^modelador_light/api/', include(v1_api.urls)),
    (r'^modelador_light/favicon.ico', generic.RedirectView.as_view(url='http://mozilla.org/favicon.ico')),

    (r'^modelador_light/$', generic.TemplateView.as_view(template_name='index.html')),



    url(r'^modelador_light/xt_pcce/lista_usuarios/$', modeladorFarmacos.views.VistaListaPCCECreadores.as_view(),
        name='creadores_lista',),

    url(r'^modelador_light/xt_pcce/lista_usuarios/(\w+)/$', modeladorFarmacos.views.VistaUsuarioCreadorPCCE.as_view()),

    url(r'^modelador_light/xt_pc/lista_usuarios/$', modeladorFarmacos.views.VistaListaPCCreadores.as_view(),
        name='creadores_lista',),

    url(r'^modelador_light/xt_pc/lista_usuarios/(\w+)/$', modeladorFarmacos.views.VistaUsuarioCreadorPC.as_view()),


    url(r'^modelador_light/xt_pc/lista_pendientes/$', modeladorFarmacos.views.VistaPorRevisarPC.as_view(),
        name='lista_pendientes',),


    url(r'^modelador_light/xt_pcce/lista_pendientes/$', modeladorFarmacos.views.VistaPorRevisarPCCE.as_view(),
        name='lista_pendientes',),


##Vistas Para Creacion de Nuevos Bioequivalentes
    url(r'^modelador_light/bioeq/$', modeladorFarmacos.views.VistaBioequivalente.as_view(),
        name='bioeq-lista',),

    url(r'^modelador_light/admin/modeladorFarmacos/xt_bioequivalente/add/$', generic.CreateView.as_view(model=xt_bioequivalente, form_class=bioeqForm, template_name='modeladorFarmacos/crea_bioequivalente.html'),
        name='bioeq-nuevo',),

    url(r'^modelador_light/admin/modeladorFarmacos/xt_bioequivalente/(?P<pk>\d+)/$', modeladorFarmacos.views.EditaBioequivalente.as_view(),
        name='bioeq-editar',),


##Creacion de productos Segun Kairos
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

    ###Efectores CAS
    (r'modelador_light/efectores/imagenes/$', efectoresVistaImagenes),


    (r'^modelador_light/search-form/$', search),

##Repositorio de Documentos
    url(r'^modelador_light/subir/', ArchivosSubidosView.as_view(), name='archivo_upload'),
    url(r'^modelador_light/lista_subidos/(?P<pk>\d+)/$', ArchivoDetalleVista.as_view (),
        name='archivo_subido'),
    url(r'^modelador_light/lista_subidos/', ArchivoIndiceVista.as_view (),
        name='archivo_lista'),
    url(r'^modelador_light/media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'media'}),

##Repositorio de Casos
    url(r'^modelador_light/casos/$', ListCaseView.as_view(),
        name='case-list',),
    url(r'^modelador_light/casos/nuevo', CreateCaseView.as_view(),
        name='case-new',),
    url(r'^modelador_light/casos/editar/(?P<pk>\d+)/$', UpdateCaseView.as_view(),
        name='case-edit',),
    url(r'^modelador_light/casos/borrar/(?P<pk>\d+)/$', DeleteCaseView.as_view(),
        name='case-delete',),
    url(r'^modelador_light/casos/(?P<pk>\d+)/$', CaseView.as_view(),
        name='case-view',),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()