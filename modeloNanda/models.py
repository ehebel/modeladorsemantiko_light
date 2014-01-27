from django.db import models
from django.contrib.auth.models import User

class nanda(models.Model):
    numero = models.IntegerField()
    titulo = models.CharField(max_length=250)
    pretitulo = models.CharField(max_length=50)
    definicion = models.TextField()
    edicion = models.CharField(max_length=100)
    tituloabreviado = models.CharField("Titulo Abreviado",max_length=255, blank=True)
    observacion = models.TextField('Observaciones', blank= True,)
    revisado = models.BooleanField()
    usrmodificacion = models.ForeignKey(User, max_length=255, related_name='usrmodificacion')
    fechamodif = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['numero']

class nandaDominio(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

class nandaClase(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    dominio = models.ForeignKey(nandaDominio)
    nanda = models.ManyToManyField(nanda)
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

class nandaTipo(models.Model):
    titulo = models.CharField(max_length=40)
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

class nandaCaracteristica(models.Model):
    titulo = models.TextField()
    tipo = models.ForeignKey(nandaTipo)
    nanda = models.ForeignKey(nanda)
    subtipo = models.CharField(max_length=40, blank=True)
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

class nandaValoracion(models.Model):
    LOGICA_OPCIONES = (
        ('=','Igual a'),
        ('<>','Distinto a'),
        ('<','Menor a'),
        ('<=','Menor o igual a'),
        ('>','Mayor a'),
        ('>=','Mayor o igual a'),
        )
    titulo = models.CharField(max_length=100)
    entidad = models.CharField(max_length=100)
    logica = models.CharField(max_length= 10, choices=LOGICA_OPCIONES, default='=')
    valor = models.CharField(max_length=5)
    nanda = models.ManyToManyField(nanda)
    def __unicode__(self):
        return self.titulo
    class Meta:
        ordering=['id']

