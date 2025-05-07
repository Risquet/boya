from django.db import models
from django.contrib.auth.models import AbstractUser


# Parameter buoys can measure
class Parameter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name="Nombre", max_length=100)
    fullname = models.CharField(verbose_name="Nombre", max_length=100)
    description = models.TextField(verbose_name="Descripción")
    min = models.FloatField(verbose_name="Min", blank=True, null=True)
    max = models.FloatField(verbose_name="Max", blank=True, null=True)
    uom = models.CharField(verbose_name="Unidad de medida", max_length=100)
    active = models.BooleanField(verbose_name="Activo", default=True)
    def __str__(self):
        return str(self.id) + ' - ' + self.name
    
    class Meta:
        ordering = ['id']
        verbose_name = 'Parámetro'
        verbose_name_plural = 'Parámetros'

# Create your models here.
class Buoy(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name="Nombre", max_length=100)
    lat = models.CharField(verbose_name="Latitud")
    lon = models.CharField(verbose_name="Longitud")
    gsm = models.BooleanField(verbose_name="Coordenadas GSM", default=False)
    model = models.CharField(null=True, blank=True, verbose_name="Modelo", max_length=100)
    manufacturer = models.CharField(null=True, blank=True, verbose_name="Fabricante", max_length=100)
    depth = models.FloatField(null=True, blank=True, verbose_name="Profundidad")
    img = models.ImageField(verbose_name="Imagen", upload_to='static/buoys', blank=True, null=True)
    plans = models.ImageField(verbose_name="Planos de Instalación", upload_to='static/buoys', blank=True, null=True)
    active = models.BooleanField(verbose_name="Activo", default=True)
    parameters = models.ManyToManyField(Parameter, blank=True, verbose_name="Parámetros")
    def __str__(self):
        return str(self.id) + ' - ' + self.name

    class Meta:
        ordering = ['id']
        verbose_name = 'Boya'
        verbose_name_plural = 'Boyas'
 

# Data measured by buoys
class Data(models.Model):
    buoy = models.ForeignKey(Buoy, verbose_name="Boya", on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name="Parámetro", on_delete=models.CASCADE)
    value = models.FloatField(verbose_name="Valor", null=True, blank=True)
    timestamp = models.BigIntegerField(verbose_name="Fecha")
    errors = models.TextField(verbose_name="Errores", null=True, blank=True)
    def __str__(self):
        return str(self.id) + ' - ' + str(self.buoy) + ' - ' + str(self.parameter) + ' - ' + str(self.value) + ' - ' + str(self.timestamp)
    
    class Meta:
        unique_together = (('buoy_id', 'parameter_id', 'timestamp'),)
        verbose_name = 'Dato'
        verbose_name_plural = 'Datos'


# Errors detected in buoys data
class ActionItems(models.Model):
    id = models.AutoField(primary_key=True)
    buoy = models.ForeignKey(Buoy, on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE)
    error = models.TextField()
    timestamp = models.BigIntegerField(null=True, blank=True)
    def __str__(self):
        return str(self.id) + ' - ' + str(self.buoy) + ' - ' + str(self.parameter) + ' - ' + str(self.timestamp)
    
    class Meta:
        ordering = ['buoy_id', 'parameter_id', 'timestamp']
        verbose_name = 'Acción'
        verbose_name_plural = 'Acciones'


# Upload data job
class UploadDataJob(models.Model):
    id = models.AutoField(primary_key=True)
    buoy = models.ForeignKey(Buoy, on_delete=models.CASCADE)
    current = models.IntegerField()
    total = models.IntegerField()
    status = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return str(self.id) + ' - ' + str(self.buoy) + ' - ' + str(self.status)
    
    class Meta:
        verbose_name = 'Carga'
        verbose_name_plural = 'Cargas'


# Override default auth.User model
class ApplicationUser(AbstractUser):
    username = models.CharField('Nombre de Usuario', unique=True, blank=False, max_length=50)
    email = models.EmailField('Correo Electrónico', unique=True, blank=False)
    first_name = models.CharField('Nombre', max_length=128)
    last_name = models.CharField('Apellidos', max_length=128)
    company = models.CharField('Entidad', max_length=128, blank=True, null=True)
    is_active = models.BooleanField('Activo', default=False)
    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = "Usuario"

    @property
    def fullname(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.username})'

# news model
class News(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField('Título', max_length=100)
    content = models.TextField('Contenido')
    date = models.DateTimeField('Fecha', auto_now_add=True)
    img = models.ImageField('Imagen', upload_to='static/news', blank=True, null=True)
    def __str__(self):
        return str(self.id) + ' - ' + self.title
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Noticia'
        verbose_name_plural = 'Noticias'