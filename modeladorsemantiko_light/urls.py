from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:

from django.views import generic

import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
admin.autodiscover()

from modeloNanda.api import EntryResource, UserResource
from tastypie.api import Api


v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(EntryResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'modeladorsemantiko_light.views.home', name='home'),
    # url(r'^modeladorsemantiko_light/', include('modeladorsemantiko_light.foo.urls')),
    url(r'^autocomplete/', include('autocomplete_light.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    (r'^api/', include(v1_api.urls)),
    (r'^favicon.ico', generic.RedirectView.as_view(url='http://mozilla.org/favicon.ico')),

    (r'^$', generic.TemplateView.as_view(template_name='index.html'))

)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()