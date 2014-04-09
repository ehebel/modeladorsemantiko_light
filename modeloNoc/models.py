from django.db import models
from modeloNic.models import nic
from modeloNanda.models import nanda


# Create your models here.
class noc(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    edicion = models.CharField(max_length=40)
    tituloabreviado = models.CharField("Titulo Abreviado",max_length=255, blank=True)
    observacion = models.TextField('Observaciones', blank= True,)
    revisado = models.BooleanField()
    nanda = models.ManyToManyField(nanda, through='relacionNandaNoc')
    nic = models.ManyToManyField(nic, through='relacionNicNoc')
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

class nocDominio(models.Model):
    letra = models.CharField(max_length=10)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

class nocClase(models.Model):
    letra = models.CharField(max_length=10)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    dominio= models.ForeignKey(nocDominio)
    noc = models.ManyToManyField(noc)
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

class nocEscala(models.Model):
    letra = models.CharField(max_length=10)
    titulo = models.CharField(max_length=100)
    codigo1 = models.CharField(max_length=100)
    codigo2 = models.CharField(max_length=100)
    codigo3 = models.CharField(max_length=100)
    codigo4 = models.CharField(max_length=100)
    codigo5 = models.CharField(max_length=100)
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

class nocEspecialidad(models.Model):
    titulo = models.CharField(max_length=100)
    noc = models.ManyToManyField(noc)
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

class nocIndicador(models.Model):
    incadorid = models.IntegerField()
    titulo = models.CharField(max_length=100)
    noc = models.ForeignKey(noc)
    escala = models.ForeignKey(nocEscala)
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

class prioridad(models.Model):
    titulo = models.CharField(max_length=100)
    def __unicode__(self):
        return self.titulo

class relacionNandaNoc(models.Model):
    noc = models.ForeignKey(noc)
    nanda = models.ForeignKey(nanda)
    prioridad = models.ForeignKey(prioridad)


class relacionNicNoc(models.Model):
    noc = models.ForeignKey(noc)
    nic = models.ForeignKey(nic)
    prioridad = models.ForeignKey(prioridad)