from django.db import models

# Create your models here.
class ArchivoSubido(models.Model):
    archivo = models.FileField(upload_to='videos/%Y/%m')