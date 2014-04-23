__author__ = 'ehebel'
import autocomplete_light
autocomplete_light.autodiscover()
from django.forms import TextInput
from django.contrib import admin
admin.autodiscover()
from modeladorFarmacos.models import *

import csv
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import FieldListFilter, SimpleListFilter
from django.utils.encoding import force_unicode

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

##Funciones de ADMIN

class EditLinkToInlineObject(object):
    def editar(self, instance):
        url = reverse('admin:%s_%s_change' % (
            instance._meta.app_label,  instance._meta.module_name),  args=[instance.pk] )
        if instance.pk:
            return mark_safe(u'<a href="{u}">editar</a>'.format(u=url))
        else:
            return ''


class UsuarioFilter(SimpleListFilter):
    title = 'Usuario creador' # or use _('country') for translated title
    parameter_name = 'usuario'

    def lookups(self, request, model_admin):
        usuarios = set([c.usuario_creador for c in model_admin.model.objects.all()])
        return [(c.id, c.username) for c in usuarios]

        # You can also use hardcoded model name like "Country" instead of
        # "model_admin.model" if this is not direct foreign key filter

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(usuario_creador__id__exact=self.value())
        else:
            return queryset

class IsNullFieldListFilter(FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '%s__isnull' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        super(IsNullFieldListFilter, self).__init__(field,
            request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def choices(self, cl):
        for lookup, title in (
            (None, _('All')),
            ('False', _('Con Elementos')),
            ('True', _('Sin Elementos'))):
            yield {
                'selected': self.lookup_val == lookup,
                'query_string': cl.get_query_string({
                    self.lookup_kwarg: lookup,
                    }),
                'display': title,
                }

def export_as_csv(modeladmin, request, queryset):
    """
    Generic csv export admin action.
    """
    if not request.user.is_staff:
        raise PermissionDenied
    opts = modeladmin.model._meta
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')
    writer = csv.writer(response, delimiter=';')
    field_names = [field.name for field in opts.fields]
    # Write a first row with header information
    writer.writerow(field_names)
    # Write data rows
    for obj in queryset:
        values = []
        for field in field_names:
            value = (getattr(obj, field))
            if callable(value):
                try:
                    value = value() or ''
                except:
                    value = 'Error retrieving value'
            if value is None:
                value = ''
            values.append(unicode(value).encode('utf-8'))
        writer.writerow(values)
        #writer.writerow([getattr(obj, field) for field in field_names])
    return response
export_as_csv.short_description = "Exportar elementos seleccionados como CSV"



###Inicio de InLines###

class ProductoComercialInline(EditLinkToInlineObject, admin.TabularInline):
    model = xt_pc
#    form = autocomplete_light.modelform_factory(xt_pc)
    fields = ['descripcion','id_xt_lab','get_pcce', 'editar',]
    ordering = ['id_xt_lab']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'80'})},
        }
    readonly_fields = ('descripcion','id_xt_lab','get_pcce', 'editar',)
    extra = 0

class pcceInLine(admin.TabularInline):
    pass
    model = xt_pcce
    form = autocomplete_light.modelform_factory(xt_pcce)
    fields = ['descripcion','id_xt_mcce']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'80'})},
        }
    extra = 0
    #readonly_fields = ['descripcion','id_xt_mcce']


class SustanciaClinicoInline(admin.TabularInline):
    model = xt_mc.rel_mc_sust.through
    form = autocomplete_light.modelform_factory(rel_mc_sust)
    radio_fields = {
        "estado": admin.HORIZONTAL}
    extra = 1

class SustanciaBasicoInline(admin.TabularInline):
    model = xt_mb.rel_xt_sust.through
    form = autocomplete_light.modelform_factory(rel_xt_mb_xt_sust)
    radio_fields = {
        "estado": admin.HORIZONTAL}
    extra = 1

class bioeqAdminInline(admin.TabularInline):
    model = xt_bioequivalente
    form = autocomplete_light.modelform_factory(xt_bioequivalente)
    fk_name = 'referencia'
    extra = 1

    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

        instance = form.save(commit=False)
        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod = request.user
        instance.usuario_ult_mod = request.user
        instance.save()
        form.save_m2m()
        return instance


#
##Inicia ADMIN de modelos Completos
##Para mejorar facilidad de busqueda
#

class xt_sustanciaAdmin (admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(xt_sustancia)
    list_display = ['id_xt_sust','descripcion'
        ,'dci'
        ,'riesgo_teratogenico']
    list_filter = ['revisado','consultar','estado','riesgo_teratogenico'
        ,('dci', IsNullFieldListFilter)
    ]
    search_fields = ['descripcion','id_xt_sust']
    ordering = ['descripcion',]

    def add_view(self, request, *args, **kwargs):
        result = super(xt_sustanciaAdmin, self).add_view(request, *args, **kwargs )
        request.session['filtered'] =  None
        return result

    def change_view(self, request, object_id, form_url='', extra_context=None):

        result = super(xt_sustanciaAdmin, self).change_view(request, object_id, form_url, extra_context )

        ref = request.META.get('HTTP_REFERER', '')
        if ref.find('?') != -1:
            request.session['filtered'] =  ref

        if request.POST.has_key('_save'):
            try:
                if request.session['filtered'] is not None:
                    result['Location'] = request.session['filtered']
                    request.session['filtered'] = None
            except:
                pass

        return result

    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        if request.POST.has_key("_viewnext"):
            msg = (_('The %(name)s "%(obj)s" was changed successfully.') %
                   {'name': force_unicode(obj._meta.verbose_name),
                    'obj': force_unicode(obj)})
            next = obj.__class__.objects.filter(id_xt_sust__gt=obj.id_xt_sust).order_by('id_xt_sust')[:1]
            if next:
                self.message_user(request, msg)
                return HttpResponseRedirect("../%s/" % next[0].pk)
        return super(xt_sustanciaAdmin, self).response_change(request, obj)

    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

        instance = form.save(commit=False)
        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod = request.user
        instance.usuario_ult_mod = request.user
        instance.save()
        form.save_m2m()
        return instance

    def save_formset(self, request, form, formset, change):

        def set_user(instance):
            if not instance.usuario_ult_mod:
                instance.usuario_ult_mod = request.user
            instance.usuario_ult_mod = request.user
            instance.save()
        if formset.model == xt_sustancia:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()

    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(xt_sustanciaAdmin,self).changelist_view(request, extra_context=extra_context)

#admin.site.register(xt_sustancia,xt_sustanciaAdmin)


class mcAdmin (admin.ModelAdmin):
    actions = [export_as_csv]
    form = autocomplete_light.modelform_factory(xt_mc)

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100'})},
        models.URLField: {'widget': TextInput(attrs={'size':'100'})}
    }

    inlines = [SustanciaClinicoInline,ProductoComercialInline]

    search_fields = ['descripcion','id_xt_mc']

    list_display = ['id_xt_mc','descripcion'
        ,'termino_autogenerado'
                    #,'med_basico'
                    #,'get_sustancia'
        ,'get_pc'
        ,'get_atc'
        ,'estado'
    ]

    list_filter = ['revisado','consultar','estado'
        ,('med_basico', IsNullFieldListFilter)
        ,('atc_code', IsNullFieldListFilter)
    ]


    list_display_links = ['id_xt_mc','descripcion']

    readonly_fields=('id_xt_mc','termino_autogenerado',)

    radio_fields = {
        "estado": admin.HORIZONTAL
        ,"consultar": admin.HORIZONTAL
        ,"revisado": admin.HORIZONTAL
        ,"tipo_forma_farm": admin.HORIZONTAL
    }

    fieldsets = (
        (None, {
            'fields': ('descripcion','termino_autogenerado','creac_nombre', 'sensible_mayusc', 'med_basico'
                       , 'estado_prescripcion','estado','revisado','consultar'
                       ,'tipo_forma_farm'
                       ,'u_logistica_cant','u_logistica_u','unidosis_asist_cant','unidosis_asist_u','volumen_total_cant'
                       ,'volumen_total_u','forma_farmaceutica_agrup','condicion_venta','atc_code','medlineplus_ulr','observacion'
                       ,
                )
        }),
        ('Opciones Avanzadas', {
            'classes': ('collapse',),
            'fields': ('sn_descriptionid', 'sn_term', 'hiba_descriptionid','hiba_term'
                       ,'cl_concepto',)
        }),
        )

    def add_view(self, request, *args, **kwargs):
        result = super(mcAdmin, self).add_view(request, *args, **kwargs )
        request.session['filtered'] =  None
        return result

    def change_view(self, request, object_id, form_url='', extra_context=None):

        result = super(mcAdmin, self).change_view(request, object_id, form_url, extra_context )

        ref = request.META.get('HTTP_REFERER', '')
        if ref.find('?') != -1:
            request.session['filtered'] =  ref

        if request.POST.has_key('_save'):
            try:
                if request.session['filtered'] is not None:
                    result['Location'] = request.session['filtered']
                    request.session['filtered'] = None
            except:
                pass

        return result

    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        if request.POST.has_key("_viewnext"):
            msg = (_('The %(name)s "%(obj)s" was changed successfully.') %
                   {'name': force_unicode(obj._meta.verbose_name),
                    'obj': force_unicode(obj)})
            next = obj.__class__.objects.filter(id_xt_mc__gt=obj.id_xt_mc).order_by('id_xt_mc')[:1]
            if next:
                self.message_user(request, msg)
                return HttpResponseRedirect("../%s/" % next[0].pk)
        return super(mcAdmin, self).response_change(request, obj)

    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

        instance = form.save(commit=False)
        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod = request.user
        instance.usuario_ult_mod = request.user
        instance.save()
        form.save_m2m()
        return instance

    def save_formset(self, request, form, formset, change):
        def set_user(instance):
            if not instance.usuario_ult_mod:
                instance.usuario_ult_mod = request.user
            instance.usuario_ult_mod = request.user
            instance.save()
        if formset.model == xt_mc:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()

    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(mcAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(xt_mc,  mcAdmin)



class mbAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100'})}}
    form = autocomplete_light.modelform_factory(xt_mb)
    inlines = [SustanciaBasicoInline,]
    ordering = ['descripcion',]
    search_fields = ['descripcion','xt_id_mb']
    list_display = ['xt_id_mb','descripcion','get_sustancia','estado','sensible_mayusc']
    list_filter = ['revisado','consultar','estado']
    list_display_links = ['xt_id_mb','descripcion']
    actions = [export_as_csv]
    readonly_fields=('xt_id_mb',)

    fieldsets = (
        (None, {
            'fields': ('descripcion','creac_nombre','sensible_mayusc','estado', 'revisado', 'consultar', 'observacion')
        }),
        ('Opciones Avanzadas', {
            'classes': ('collapse',),
            'fields': ('sn_descriptionid','sn_term','hiba_descriptionid', 'hiba_term', 'cl_concepto')
        }),
        )

    radio_fields = {
        "estado": admin.HORIZONTAL
        ,"consultar": admin.HORIZONTAL
        ,"revisado": admin.HORIZONTAL
    }
    def add_view(self, request, *args, **kwargs):
        result = super(mbAdmin, self).add_view(request, *args, **kwargs )
        request.session['filtered'] =  None
        return result

    def change_view(self, request, object_id, form_url='', extra_context=None):

        result = super(mbAdmin, self).change_view(request, object_id, form_url, extra_context )

        ref = request.META.get('HTTP_REFERER', '')
        if ref.find('?') != -1:
            request.session['filtered'] =  ref

        if request.POST.has_key('_save'):
            try:
                if request.session['filtered'] is not None:
                    result['Location'] = request.session['filtered']
                    request.session['filtered'] = None
            except:
                pass

        return result

    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        if request.POST.has_key("_viewnext"):
            msg = (_('The %(name)s "%(obj)s" was changed successfully.') %
                   {'name': force_unicode(obj._meta.verbose_name),
                    'obj': force_unicode(obj)})
            next = obj.__class__.objects.filter(xt_id_mb__gt=obj.xt_id_mb).order_by('xt_id_mb')[:1]
            if next:
                self.message_user(request, msg)
                return HttpResponseRedirect("../%s/" % next[0].pk)
        return super(mbAdmin, self).response_change(request, obj)

    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

        instance = form.save(commit=False)
        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod = request.user
        instance.usuario_ult_mod = request.user
        instance.save()
        form.save_m2m()
        return instance
    def save_formset(self, request, form, formset, change):
        def set_user(instance):
            if not instance.usuario_ult_mod:
                instance.usuario_ult_mod = request.user
            instance.usuario_ult_mod = request.user
            instance.save()
        if formset.model == xt_mb:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()

    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(mbAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(xt_mb,  mbAdmin)



class mcceAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100'})}
    }
    form = autocomplete_light.modelform_factory(xt_mcce)

    list_display = ['id_xt_mcce','descripcion'
        ,'tipo'
                    #        ,'id_xt_mc'
        ,'cantidad'
                    #        ,'unidad_medida_cant'
        ,'volumen_total_cant'
                    #        ,'volumen_total_u'
    ]

    list_filter = ['revisado','consultar','estado','tipo','unidad_medida_cant','volumen_total_u'
    ]
    search_fields = ['descripcion','id_xt_mcce']
    readonly_fields=('id_xt_mcce',)

    actions = [export_as_csv]
    radio_fields = {
        "estado": admin.HORIZONTAL
        ,"consultar": admin.HORIZONTAL
        ,"revisado": admin.HORIZONTAL
    }

    fieldsets = (
        (None, {
            'fields': ('descripcion', 'sensible_mayusc', 'creac_nombre'
                       ,'estado','revisado','consultar','tipo','id_xt_mc'
                       ,'cantidad','unidad_medida_cant','pack_multi_cant','pack_multi_u'
                       ,'volumen_total_cant','volumen_total_u'
                       ,'observacion')
        }),
        ('Opciones Avanzadas', {
            'classes': ('collapse',),
            'fields': ('hiba_descriptionid', 'hiba_term', 'cl_concepto')
        }),
        )

    def add_view(self, request, *args, **kwargs):
        result = super(mcceAdmin, self).add_view(request, *args, **kwargs )
        request.session['filtered'] =  None
        return result
    def change_view(self, request, object_id, form_url='', extra_context=None):

        result = super(mcceAdmin, self).change_view(request, object_id, form_url, extra_context )

        ref = request.META.get('HTTP_REFERER', '')
        if ref.find('?') != -1:
            request.session['filtered'] =  ref

        if request.POST.has_key('_save'):
            try:
                if request.session['filtered'] is not None:
                    result['Location'] = request.session['filtered']
                    request.session['filtered'] = None
            except:
                pass

        return result
    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        if request.POST.has_key("_viewnext"):
            msg = (_('The %(name)s "%(obj)s" was changed successfully.') %
                   {'name': force_unicode(obj._meta.verbose_name),
                    'obj': force_unicode(obj)})
            next = obj.__class__.objects.filter(id_xt_mcce__gt=obj.id_xt_mcce).order_by('id_xt_mcce')[:1]
            if next:
                self.message_user(request, msg)
                return HttpResponseRedirect("../%s/" % next[0].pk)
        return super(mcceAdmin, self).response_change(request, obj)
    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

        instance = form.save(commit=False)
        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod = request.user
        instance.usuario_ult_mod = request.user
        instance.save()
        form.save_m2m()
        return instance
    def save_formset(self, request, form, formset, change):
        def set_user(instance):
            if not instance.usuario_ult_mod:
                instance.usuario_ult_mod = request.user
            instance.usuario_ult_mod = request.user
            instance.save()
        if formset.model == xt_mcce:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()

    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(mcceAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(xt_mcce,mcceAdmin)


#
class pcAdmin(admin.ModelAdmin):
#    exclude = ('revisado',)
    actions = [export_as_csv]
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100'})}
    }
    inlines = [bioeqAdminInline
                , pcceInLine
                 ]
    search_fields = ['descripcion','id_xt_pc']
    list_display = ['id_xt_pc','descripcion','id_xt_mc','id_xt_lab'
                ,'forma_farm_extendida'
#        ,'usuario_creador'
#        ,'get_pcce'
        ] #TODO BOOL Bioequivalente
    list_filter = ['estado','revisado','consultar'
        ,'usuario_creador__username'
                   #        , UsuarioFilter
        ,('id_xt_mc', IsNullFieldListFilter)
        ,('id_xt_lab', IsNullFieldListFilter)
        ,'fecha_ult_mod'
        ,'forma_farm_extendida__estado'

    ] #TODO BOOL Observacion
    form = autocomplete_light.modelform_factory(xt_pc)

    fieldsets = (
        (None, {
            'fields': ('descripcion', 'descripcion_abreviada', 'sensible_mayusc', 'creac_nombre'
                       ,'estado'
                       ,'revisado'
                       ,'consultar'
                       ,'comercial_cl'
                       ,'forma_farm_extendida','sabor','id_xt_fp'
                       ,'id_xt_mc','id_xt_lab'
                       ,'reg_isp','reg_isp_num'
#                       ,'reg_isp_ano'
                       ,'observacion')
        }),
        ('Avanzados', {
            'classes': ('collapse',),
            'fields': ('hiba_descriptionid', 'hiba_term','cl_concepto')
        }),
        )

    readonly_fields=('id_xt_pc',)
    radio_fields = {
        "estado": admin.HORIZONTAL
        ,"consultar": admin.HORIZONTAL
        ,"revisado": admin.HORIZONTAL
        ,'comercial_cl': admin.HORIZONTAL
        ,'reg_isp' : admin.HORIZONTAL
    }
    def add_view(self, request, *args, **kwargs):
        result = super(pcAdmin, self).add_view(request, *args, **kwargs )
        request.session['filtered'] =  None
        return result

    def change_view(self, request, object_id, form_url='', extra_context=None):

        result = super(pcAdmin, self).change_view(request, object_id, form_url, extra_context )

        ref = request.META.get('HTTP_REFERER', '')
        if ref.find('?') != -1:
            request.session['filtered'] =  ref

        if request.POST.has_key('_save'):
            try:
                if request.session['filtered'] is not None:
                    result['Location'] = request.session['filtered']
                    request.session['filtered'] = None
            except:
                pass

        elif request.POST.has_key('_viewnext'):
            msg = (_('The %(name)s "%(obj)s" was changed successfully.') %
                   {'name': force_unicode(object_id),
                    'obj': force_unicode(object_id)})

            try:
                if request.session['filtered'] is not None:

                    qs = self.model._base_manager.get_query_set().order_by('id_xt_pc')
                    next = object_id.__class__.objects.filter(id_xt_pc__gt=object_id.id_xt_pc, id_xt_pc__in=qs).order_by('id_xt_pc')[:1]
                    if next:
                        self.message_user(request, msg)
                        return HttpResponseRedirect("../%s/" % next[0].object_id)
                    #                    result['Location'] = request.session['filtered']

                    request.session['filtered'] = None

            except:
                pass

        return result

    #    def changelist_view(self, request, extra_context=None):
    #        super(pcAdmin,self).changelist_view(request, extra_context)

    #    def response_change(self, request, obj):
    #        """
    #        Determines the HttpResponse for the change_view stage.
    #        """
    #        if request.POST.has_key("_viewnext"):
    #            msg = (_('The %(name)s "%(obj)s" was changed successfully.') %
    #                   {'name': force_unicode(obj._meta.verbose_name),
    #                    'obj': force_unicode(obj)})
    #            next = obj.__class__.objects.filter(id_xt_pc__gt=obj.id_xt_pc).order_by('id_xt_pc')[:1]
    #            if next:
    #                self.message_user(request, msg)
    #                return HttpResponseRedirect("../%s/" % next[0].pk)
    #        return super(pcAdmin, self).response_change(request, obj)

    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

        instance = form.save(commit=False)
        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod = request.user
        instance.usuario_ult_mod = request.user
        instance.save()
        form.save_m2m()
        return instance

    def save_formset(self, request, form, formset, change):
        def set_user(instance):
            if not instance.usuario_ult_mod:
                instance.usuario_ult_mod = request.user
            instance.usuario_ult_mod = request.user
            instance.save()
        if formset.model == xt_pc:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()

    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(pcAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(xt_pc , pcAdmin)

#
class pcceAdmin(admin.ModelAdmin):
#    exclude = ('revisado',)
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'170'})}
    }
    form = autocomplete_light.modelform_factory(xt_pcce)
    list_filter = ['estado','revisado','consultar'
                   #        ,UsuarioFilter
        ,'usuario_creador__username'
        ,('id_xt_mcce', IsNullFieldListFilter)
        ,('id_presentacion_kairos', IsNullFieldListFilter)
    ] #TODO BOOL Observacion
    fieldsets = (
        (None, {
            'fields': ('descripcion', 'desc_abreviada', 'sensible_mayusc', 'creac_nombre'
                       ,'estado','revisado','consultar','id_xt_pc','id_xt_mcce','id_presentacion_kairos','codigo_dbnet','observacion')
        }),
        ('Avanzandos', {
            'classes': ('collapse',),
            'fields': ('pack_cant', 'pack_u', 'gtin_gs1','existencia_gs1','codigo_cenabast','hiba_descriptionid'
                       ,'hiba_term','cl_concepto','id_xt_pcce')
        }),
        )

    list_display = ['id_xt_pcce'
                    ,'descripcion'
#                    ,'usuario_creador'
                     ]
    search_fields = ['descripcion','id_xt_pcce']
    readonly_fields=('id_xt_pcce',)
    actions = [export_as_csv]
    radio_fields = {
        "estado": admin.HORIZONTAL
        ,"consultar": admin.HORIZONTAL
        ,"revisado": admin.HORIZONTAL
    }
    def add_view(self, request, *args, **kwargs):
        result = super(pcceAdmin, self).add_view(request, *args, **kwargs )
        request.session['filtered'] =  None
        return result

    def change_view(self, request, object_id, form_url='', extra_context=None):

        result = super(pcceAdmin, self).change_view(request, object_id, form_url, extra_context )

        ref = request.META.get('HTTP_REFERER', '')
        if ref.find('?') != -1:
            request.session['filtered'] =  ref

        if request.POST.has_key('_save'):
            try:
                if request.session['filtered'] is not None:
                    result['Location'] = request.session['filtered']
                    request.session['filtered'] = None
            except:
                pass

        return result

    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        if request.POST.has_key("_viewnext"):
            msg = (_('The %(name)s "%(obj)s" was changed successfully.') %
                   {'name': force_unicode(obj._meta.verbose_name),
                    'obj': force_unicode(obj)})
            next = obj.__class__.objects.filter(id_xt_pcce__gt=obj.id_xt_pcce).order_by('id_xt_pcce')[:1]
            if next:
                self.message_user(request, msg)
                return HttpResponseRedirect("../%s/" % next[0].pk)
        return super(pcceAdmin, self).response_change(request, obj)

    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

        instance = form.save(commit=False)
        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod = request.user
        instance.usuario_ult_mod = request.user
        instance.save()
        form.save_m2m()
        return instance

    def save_formset(self, request, form, formset, change):
        def set_user(instance):
            if not instance.usuario_ult_mod:
                instance.usuario_ult_mod = request.user
            instance.usuario_ult_mod = request.user
            instance.save()
        if formset.model == xt_mc:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()

    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(pcceAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(xt_pcce,pcceAdmin)

class xtlabAdmin(admin.ModelAdmin):
    list_display = ['descripcion','desc_abrev','estado','sensible_mayusc']
    list_filter = ['revisado','consultar','estado']
    search_fields = ['descripcion',]

    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        if request.POST.has_key("_viewnext"):
            msg = (_('The %(name)s "%(obj)s" was changed successfully.') %
                   {'name': force_unicode(obj._meta.verbose_name),
                    'obj': force_unicode(obj)})
            next = obj.__class__.objects.filter(id_xt_lab__gt=obj.id_xt_lab).order_by('id_xt_lab')[:1]
            if next:
                self.message_user(request, msg)
                return HttpResponseRedirect("../%s/" % next[0].pk)
        return super(xtlabAdmin, self).response_change(request, obj)

    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

        instance = form.save(commit=False)
        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod = request.user
        instance.usuario_ult_mod = request.user
        instance.save()
        form.save_m2m()
        return instance
    def save_formset(self, request, form, formset, change):
        def set_user(instance):
            if not instance.usuario_ult_mod:
                instance.usuario_ult_mod = request.user
            instance.usuario_ult_mod = request.user
            instance.save()
        if formset.model == xt_mc:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()

    def add_view(self, request, *args, **kwargs):
        result = super(xtlabAdmin, self).add_view(request, *args, **kwargs )
        request.session['filtered'] =  None
        return result

    def change_view(self, request, object_id, form_url='', extra_context=None):

        result = super(xtlabAdmin, self).change_view(request, object_id, form_url, extra_context )

        ref = request.META.get('HTTP_REFERER', '')
        if ref.find('?') != -1:
            request.session['filtered'] =  ref

        if request.POST.has_key('_save'):
            try:
                if request.session['filtered'] is not None:
                    result['Location'] = request.session['filtered']
                    request.session['filtered'] = None
            except:
                pass

        return result

    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(xtlabAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(xt_laboratorio,xtlabAdmin)

class uduAdmin(admin.ModelAdmin):
    list_display = ['pk','descripcion','estado']
    search_fields = ['descripcion']
    list_filter = ['estado']
    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(uduAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(xt_unidad_dosis_unitaria,uduAdmin)


class umuAdmin(admin.ModelAdmin):
    list_display = ['pk','descripcion','estado']
    search_fields = ['descripcion']
    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(umuAdmin,self).changelist_view(request, extra_context=extra_context)


admin.site.register(xt_unidad_medida_unitaria,umuAdmin)


class ffAdmin(admin.ModelAdmin):
    list_display = ['descripcion','forma_agrupada','estado']
    list_filter = ['estado','forma_agrupada']
    search_fields = ['descripcion']

    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

        instance = form.save(commit=False)

        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod = request.user
        instance.usuario_ult_mod = request.user
        instance.save()
        form.save_m2m()
        return instance

    def save_formset(self, request, form, formset, change):
        def set_user(instance):
            if not instance.usuario_ult_mod:
                instance.usuario_ult_mod = request.user
            instance.usuario_ult_mod = request.user
            instance.save()
        if formset.model == xt_forma_farm:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()
    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(ffAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(xt_forma_farm,ffAdmin)


class condVentaAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()
    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(condVentaAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(xt_condicion_venta,condVentaAdmin)

class upAdmin(admin.ModelAdmin):
    list_display = ['id_unidad_potencia','descripcion','estado']
    search_fields = ['descripcion']
    #    ordering = ['id_unidad_potencia',]
    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

        instance = form.save(commit=False)
        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod = request.user
        instance.usuario_ult_mod = request.user
        instance.save()
        form.save_m2m()
        return instance
    def save_formset(self, request, form, formset, change):
        def set_user(instance):
            if not instance.usuario_ult_mod:
                instance.usuario_ult_mod = request.user
            instance.usuario_ult_mod = request.user
            instance.save()
        if formset.model == xt_mc:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()
    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(upAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(xt_unidad_potencia,upAdmin)


class gfpAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

        instance = form.save(commit=False)
        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod = request.user
        instance.usuario_ult_mod = request.user
        instance.save()
        form.save_m2m()
        return instance
    def save_formset(self, request, form, formset, change):
        def set_user(instance):
            if not instance.usuario_ult_mod:
                instance.usuario_ult_mod = request.user
            instance.usuario_ult_mod = request.user
            instance.save()
        if formset.model == xt_mc:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()
    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(gfpAdmin,self).changelist_view(request, extra_context=extra_context)


    list_display = ['descripcion','sensible_mayusc','estado']
    list_filter = ['sensible_mayusc','estado','revisado','consultar']
    search_fields = ['descripcion']

admin.site.register(xt_gfp , gfpAdmin)

class fpAdmin(admin.ModelAdmin):
    search_fields = ['descripcion']
    list_display = ['id_xt_fp', 'descripcion','id_gfp_xt']
    list_filter = ['familia_generica',('id_gfp_xt', IsNullFieldListFilter),'estado']

    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

        instance = form.save(commit=False)
        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod = request.user
        instance.usuario_ult_mod = request.user
        instance.save()
        form.save_m2m()
        return instance
    def save_formset(self, request, form, formset, change):
        def set_user(instance):
            if not instance.usuario_ult_mod:
                instance.usuario_ult_mod = request.user
            instance.usuario_ult_mod = request.user
            instance.save()
        if formset.model == xt_mc:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()
    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(fpAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(xt_fp,fpAdmin)

class bioeqAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(xt_bioequivalente)
    list_display = ['pk', 'get_referente','get_equivalente']
    search_fields = ['referencia__descripcion','bioequivalente__descripcion']
    list_filter = ['usuario_creador','usuario_ult_mod']

    def get_referente(self, obj):
        return obj.referencia.descripcion
    get_referente.short_description = 'Referente'

    def get_equivalente(self, obj):
        return obj.bioequivalente.descripcion
    get_equivalente.short_description = 'Bioequivalente'

admin.site.register(xt_bioequivalente,bioeqAdmin)

class atcAdmin(admin.ModelAdmin):
    list_display = ['cod_atc','atc_desc','n1_desc','n2_desc','n3_desc','n4_desc']
    search_fields = ['cod_atc','atc_desc','n1_desc','n2_desc','n3_desc','n4_desc']
    list_filter = ['n1_desc']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'120'})},
        }
admin.site.register(atc,atcAdmin)


class umcAdmin(admin.ModelAdmin):
    list_display = [
        'pk','descripcion','estado'
    ]
    search_fields = ['descripcion']
    list_filter = ['estado']
    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

        instance = form.save(commit=False)
        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod = request.user
        instance.usuario_ult_mod = request.user
        instance.save()
        form.save_m2m()
        return instance

    def save_formset(self, request, form, formset, change):
        def set_user(instance):
            if not instance.usuario_ult_mod:
                instance.usuario_ult_mod = request.user
            instance.usuario_ult_mod = request.user
            instance.save()
        if formset.model == xt_unidad_medida_cant:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()

    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(umcAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(xt_unidad_medida_cant,umcAdmin)


class formaAgrupadaAdmin(admin.ModelAdmin):
    search_fields = ['descripcion',]
    list_display = ['descripcion','estado']

    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

        instance = form.save(commit=False)

        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod = request.user
        instance.usuario_ult_mod = request.user
        instance.save()
        form.save_m2m()
        return instance

    def save_formset(self, request, form, formset, change):
        def set_user(instance):
            if not instance.usuario_ult_mod:
                instance.usuario_ult_mod = request.user
            instance.usuario_ult_mod = request.user
            instance.save()
        if formset.model == xt_forma_agrupada:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()
    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(formaAgrupadaAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(xt_forma_agrupada,formaAgrupadaAdmin)

class kairosTxtAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(kairos_texto_producto)
    list_display = ['id','clave']
    exclude = ('texto',)
    readonly_fields=('orden','clave','html_texto',)
admin.site.register(kairos_texto_producto, kairosTxtAdmin)



admin.site.register(kairos_lab)


class kairosProd(admin.ModelAdmin):
    search_fields = ['descripcion']
admin.site.register(kairos_productos,kairosProd)



class kairosPresAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(kairos_presentaciones)
    search_fields = ['claveproducto__descripcion','descripcion']
    #    list_display = ['descripcion','medio','estado']
    list_filter = ['estado','medio',]
admin.site.register(kairos_presentaciones,kairosPresAdmin)


class kairosPrecioAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(kairos_precio)
admin.site.register(kairos_precio,kairosPrecioAdmin)


class xtSaborAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):

        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador = request.user
        obj.save()

        instance = form.save(commit=False)
        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod = request.user
        instance.usuario_ult_mod = request.user
        instance.save()
        form.save_m2m()
        return instance
    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(xtSaborAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(xt_sabor,xtSaborAdmin)
admin.site.register(registroSanitario)


__author__ = 'ehebel'