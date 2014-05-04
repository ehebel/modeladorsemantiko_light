import autocomplete_light
autocomplete_light.autodiscover()
#from django.forms import TextInput
from django.contrib import admin
admin.autodiscover()
from maestroIndicaciones.models import *

import csv
from django.http import HttpResponse,HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import FieldListFilter, SimpleListFilter
#from django.utils.encoding import force_unicode

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse


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


class versionesAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador_id = request.user.id
        obj.save()

        instance = form.save(commit=False)
        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod_id = request.user.id
        instance.usuario_ult_mod_id = request.user.id
        instance.save()
        form.save_m2m()
        return instance

#    def add_view(self, request, *args, **kwargs):
#        result = super(versionesAdmin,self).add_view(request, *args, **kwargs )
#        request.session['filtered'] =  None
#        return result
#
#    def change_view(self, request, object_id, form_url='', extra_context=None):
#
#        result = super(versionesAdmin,self).change_view(request, object_id, form_url, extra_context )
#
#        ref = request.META.get('HTTP_REFERER', '')
#        if ref.find('?') != -1:
#            request.session['filtered'] =  ref
#
#        if request.POST.has_key('_save'):
#            try:
#                if request.session['filtered'] is not None:
#                    result['Location'] = request.session['filtered']
#                    request.session['filtered'] = None
#            except:
#                pass
#
#        return result

#################

class relgrupojerarquicoInline(admin.TabularInline):
    model = relacion_grupojerarquico
    fk_name = 'id_grupopadre'
    extra = 1

    def save_model(self, request, obj, form, change):
        if not hasattr(obj, 'usuario_creador'):
            obj.usuario_creador_id = request.user.id
        obj.save()

        instance = form.save(commit=False)
        if not hasattr(instance,'usuario_ult_mod'):
            instance.usuario_ult_mod_id = request.user.id
        instance.usuario_ult_mod_id = request.user.id
        instance.save()
        form.save_m2m()
        return instance


class descripcionAdmin(versionesAdmin):
    exclude = 'tipodescripcion','id_concepto'

admin.site.register(descripcion, descripcionAdmin)

class conceptoAdmin(versionesAdmin):
#    list_display = ['__unicode__','dominio','grupojerarquico']
    pass
admin.site.register(concepto,conceptoAdmin)


class grupojerarquicoAdmin(versionesAdmin):
    inlines = relgrupojerarquicoInline,

##  La modificacion de save_formset es necesaria para cuando el formulario tiene InLine

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, relacion_grupojerarquico): #Check if it is the correct type of inline
                if not instance.usuario_creador_id:
                    instance.usuario_creador_id = request.user.id
                else:
                    instance.usuario_ult_mod_id = request.user.id
                instance.save()

admin.site.register(grupojerarquico,grupojerarquicoAdmin)

class xt_unidadAdmin(versionesAdmin):
    ordering = ['id_unidad',]
#    readonly_fields = 'id_unidad',
    list_filter = ['estado',]
    radio_fields = {
            "creac_nombre": admin.HORIZONTAL
            ,"u_logistica": admin.HORIZONTAL
            ,"u_asistencial": admin.HORIZONTAL
            ,"u_volumen": admin.HORIZONTAL
            ,"u_potencia": admin.HORIZONTAL
            ,"u_pack": admin.HORIZONTAL
            ,"u_medida_cantidad": admin.HORIZONTAL
            ,"u_visible_prescripcion": admin.HORIZONTAL
                    }
admin.site.register(xt_unidad,xt_unidadAdmin)

class xt_laboratorioAdmin(versionesAdmin):
    pass
admin.site.register(xt_laboratorio,xt_laboratorioAdmin)

class xt_gfpAdmin(versionesAdmin):
    pass
admin.site.register(xt_gfp,xt_gfpAdmin)

class xt_fpAdmin(versionesAdmin):
    pass
admin.site.register(xt_fp,xt_fpAdmin)