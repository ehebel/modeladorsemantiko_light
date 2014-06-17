from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from snomedct.models import sct_description

OPCIONES_INSTITUCION = (
    ('CAS','Clinica Alemana Santiago'),
    ('HPH','Hospital Padre Hurtado'),
    ('CAT','Clinica Alemana Temuco'),
    )

OPCIONES_DOMINIO = (
    ('1','Cuerpo'),
    ('2','Mama'),
    ('3','MSK'),
    ('4','Pediatria'),
    ('5','Neuro'),
    ('4','Otro'),
    )

class BaseModel(models.Model):
    fecha_creacion = models.DateTimeField(null=False, auto_now_add=True)
    usuario_creador = models.ForeignKey(User, null=True, blank=False, editable=False, related_name='%(app_label)s_%(class)s_related_crea')
    fecha_ult_mod = models.DateTimeField(null=True, auto_now=True)
    usuario_ult_mod = models.ForeignKey(User, null=True, blank=False, editable=False, related_name='%(app_label)s_%(class)s_related_modif')

    class Meta:
        abstract = True

class radlex(models.Model):
    name = models.CharField(max_length=255)
    rid = models.CharField(max_length=30, primary_key=True)
    parent = models.CharField(max_length=30)
    def __unicode__(self):

        return unicode(self.name)

class caso(BaseModel):
    fechacaso = models.DateField('Fecha')
    nombre = models.CharField('Nombre',max_length=255)
    appaterno = models.CharField('Apellido Paterno',max_length=255)
    apmaterno = models.CharField('Apellido Materno',max_length=255, blank=True, null=True)
    institucion = models.CharField('Institucion',max_length=5, choices=OPCIONES_INSTITUCION)
    observacion = models.CharField('Observacion',max_length=255)
    dominio = models.CharField(choices=OPCIONES_DOMINIO,max_length=255)
    seguimiento = models.BooleanField(u'Requiere seguimiento?')
    tagging = models.ManyToManyField(sct_description, blank=True)
    url = models.URLField(blank=True)

    def __unicode__(self):

        return unicode(self.observacion)


    def get_absolute_url(self):

        return reverse('case-view', kwargs={'pk': self.id})

    class Meta:
        ordering = ["-fechacaso"]

    def get_field_values(self):
        return [field.value_to_string(self) for field in caso._meta.fields]
#
#class casoForm(ModelForm):
#    class Meta:
#        model = caso
#        fields = ('fechacaso','nombre','appaterno','apmaterno','institucion','observacion')
#        widgets = {
#            'observacion': Textarea(attrs={'cols':80, 'rows':20}),
#        }