import csv
import autocomplete_light
from django.contrib.admin import FieldListFilter, SimpleListFilter
from django.core.exceptions import PermissionDenied
from django.forms import TextInput

autocomplete_light.autodiscover()
from django.contrib import admin
admin.autodiscover()
from efectorescas.models import *
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _


from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse


class EditLinkToInlineObject(object):
    def edit_link(self, instance):
        url = reverse('admin:%s_%s_change' % (
            instance._meta.app_label,  instance._meta.module_name),  args=[instance.pk] )
        if instance.pk:
            return mark_safe(u'<a href="{u}">editar</a>'.format(u=url))
        else:
            return ''



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

class BaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.usuario_creador = request.user

        obj.usuario_ult_mod = request.user
        obj.save()


    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, concepto):
            #Check if it is the correct type of inline
                if not instance.usuario_creador:
                    instance.usuario_creador = request.user

                instance.usuario_ult_mod = request.user
                instance.save()



class DescInLine(admin.TabularInline):
    model = descripcion
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'120'})},
    }

class ConceptosAreaInline(EditLinkToInlineObject, admin.TabularInline):
    model = cas_area.conceptosporarea.through
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'120'})},
    }
    readonly_fields = ('get_efectorxarea', 'edit_link',)




class conceptoAreaInline2(admin.TabularInline):
    model = efector.codigoporarea.through
    form = autocomplete_light.modelform_factory(efector)

class ConceptAdmin(admin.ModelAdmin):
    list_filter = ['revisado','dominio','pedible',]
    list_display = ['fsn','descripciones','get_areas']
    inlines = DescInLine,ConceptosAreaInline
    actions = [export_as_csv]
    search_fields = ['fsn',]

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'120'})},
    }
    def add_view(self, request, *args, **kwargs):
        result = super(ConceptAdmin, self).add_view(request, *args, **kwargs )
        request.session['filtered'] =  None
        return result

    def change_view(self, request, object_id, form_url='', extra_context=None):

        result = super(ConceptAdmin, self).change_view(request, object_id, form_url, extra_context )

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
            next = obj.__class__.objects.filter(id__gt=obj.id).order_by('id')[:1]
            if next:
                self.message_user(request, msg)
                return HttpResponseRedirect("../%s/" % next[0].pk)
        return super(ConceptAdmin, self).response_change(request, obj)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        return super(ConceptAdmin, self).__init__(*args, **kwargs)


    def save(self, *args, **kwargs):
        kwargs['commit']=False
        obj = super(ConceptAdmin, self).save(*args, **kwargs)
        if self.request:
            obj.usuario_creador = self.request.user
        obj.save()

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
        if formset.model == concepto:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()



admin.site.register(concepto,ConceptAdmin)

#
class EfectoresAreaInline(admin.TabularInline):
    model = efector_codigoporarea
    form = autocomplete_light.modelform_factory(efector)





class efectorAdmin(admin.ModelAdmin):
#    form = autocomplete_light.modelform_factory(efector)
#    filter_vertical = ('codigoporarea',)
    inlines = EfectoresAreaInline,
    list_display = ['ExamCode','ExamName','get_conceptosporarea','get_areas']
    list_filter = ['dominio']
    search_fields = ['ExamCode','ExamName']
    actions = [export_as_csv]

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
        if formset.model == efector:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()

admin.site.register(efector,efectorAdmin)


class descripcionAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(descripcion)
    list_display = ['termino','tipodescripcion','id_concepto']
    list_filter = ['tipodescripcion']
    search_fields = ['termino',]
    actions = [export_as_csv]


    def save_model(self, request, obj, form, change):
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
        if formset.model == descripcion:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()

admin.site.register(descripcion,descripcionAdmin)




class efectorareaAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(efector_codigoporarea)

    list_display = ('id','efector'
                    ,'conceptoscasporarea'
        )
    ordering = ('id',)

    search_fields = ('efector__ExamName',)

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
        if formset.model == efector_codigoporarea:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()

admin.site.register(efector_codigoporarea,efectorareaAdmin)


class concCasAreaAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(conceptosCASporarea)
    def change_view(self, request, object_id, form_url='', extra_context=None):

        result = super(concCasAreaAdmin, self).change_view(request, object_id, form_url, extra_context )

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
            next = obj.__class__.objects.filter(id__gt=obj.conceptosCASporarea).order_by('id')[:1]
            if next:
                self.message_user(request, msg)
                return HttpResponseRedirect("../%s/" % next[0].pk)
        return super(concCasAreaAdmin, self).response_change(request, obj)

    inlines = conceptoAreaInline2,
    list_display = ['concepto'
        ,'get_efectorxarea'
        ,'area'
    ]
    list_filter = ['area']
    search_fields = ['concepto__fsn']
    ordering = ('id',)
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
        if formset.model == conceptosCASporarea:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()

admin.site.register(conceptosCASporarea ,concCasAreaAdmin)

class areasAdmin(admin.ModelAdmin):
    list_display = ['descripcion','conceptos']



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
        if formset.model == cas_area:
            instances = formset.save(commit=False)
            map(set_user, instances)
            formset.save_m2m()
            return instances
        else:
            return formset.save()

#    def save_model(self, request, obj, form, change):
#        if not change:
#            obj.usuario_creador = request.user
#
#        obj.usuario_ult_mod = request.user
#        obj.save()
#
#
#    def save_formset(self, request, form, formset, change):
#        instances = formset.save(commit=False)
#
#        for instance in instances:
#            if isinstance(instance, descripcion):
#            #Check if it is the correct type of inline
#                if not instance.usuario_creador:
#                    instance.usuario_creador = request.user
#
#                instance.usuario_ult_mod = request.user
#                instance.save()

admin.site.register(cas_area,areasAdmin)
admin.site.register(cas_lugar)




__author__ = 'ehebel'


