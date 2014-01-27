from django.db import models
from modeloNanda.models import nanda

class nic(models.Model):
    titulo = models.CharField(max_length=100)
    definicion = models.TextField()
    edicion = models.CharField(max_length=40)
    tituloabreviado = models.CharField("Titulo Abreviado",max_length=255, blank=True)
    observacion = models.TextField('Observaciones', blank= True,)
    revisado = models.BooleanField()
    nandas = models.ManyToManyField(nanda, through='relacionNandaNic')
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

class nicActividad(models.Model):
    titulo = models.TextField()
    nic = models.ForeignKey(nic)
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

class nicCampo(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

class nicClase(models.Model):
    letra = models.CharField(max_length=10)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    campo = models.ForeignKey(nicCampo)
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

class nicEspecialidad(models.Model):
    titulo = models.CharField(max_length=100)
    nic = models.ManyToManyField(nic)
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

class relacionNandaNic(models.Model):
    nanda = models.ForeignKey(nanda)
    nic = models.ForeignKey(nic)
    prioridad = models.CharField(max_length=40)
    class Meta:
        ordering=['id']