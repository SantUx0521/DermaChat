from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models import Avg

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio.')
        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, nombre, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField(null=True, blank=True) 
    estatura = models.FloatField(null=True, blank=True)
    peso = models.FloatField(null=True, blank=True)
    sexo = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Femenino')], null=True, blank=True)
    foto_perfil = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    es_dueño = models.BooleanField(default=False)
    #verificacion de email
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    email_verificado = models.BooleanField(default=False)
    token_verificacion = models.CharField(max_length=100, blank=True, null=True)
    fecha_token = models.DateTimeField(blank=True, null=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']
    
    def __str__(self):
        return self.email


class FichaBiometrica(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='ficha_biometrica', null=True, blank=True)
    altura = models.DecimalField(max_digits=5, decimal_places=2)
    peso = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Ficha de {self.usuario.nombre}"
    
class Gimnasio(models.Model):
    codigo_gym = models.AutoField(primary_key=True)
    dueño = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='gimnasios')
    nombre_gym = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=255)
    calificacion = models.FloatField(default=0)
    cantidad_resenas = models.IntegerField(default=0) 
    precio_inscripcion = models.DecimalField(max_digits=8, decimal_places=2)
    descripcion = models.TextField()
    vistas = models.IntegerField(default=0)
    imagen = models.ImageField(upload_to='gimnasios/', null=True, blank=True)

    def __str__(self):
        return self.nombre_gym

class ClienteGimnasio(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='gimnasios_inscritos')
    gimnasio = models.ForeignKey(Gimnasio, on_delete=models.CASCADE, related_name='clientes')

    class Meta:
        unique_together = ('usuario', 'gimnasio')

    def __str__(self):
        return f"{self.usuario.email} inscrito en {self.gimnasio.nombre_gym}"

class Favorito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='favoritos')
    gimnasio = models.ForeignKey(Gimnasio, on_delete=models.CASCADE, related_name='favorito_por')

    class Meta:
        unique_together = ('usuario', 'gimnasio')

    def __str__(self):
        return f"{self.usuario.email} → {self.gimnasio.nombre_gym}"

class Rutina(models.Model):
    gimnasio = models.ForeignKey(Gimnasio, on_delete=models.CASCADE, related_name='rutinas')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    duracion = models.IntegerField(help_text="Duración en minutos")
    nivel = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
    
class Maquina(models.Model):
    gimnasio = models.ForeignKey(Gimnasio, on_delete=models.CASCADE, related_name='maquinas')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre


class Inventario(models.Model):
    codigo_prod = models.AutoField(primary_key=True)
    gimnasio = models.ForeignKey(Gimnasio, on_delete=models.CASCADE, related_name='productos')
    nombre_prod = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.nombre_prod
    
class Reseña(models.Model):
    gimnasio = models.ForeignKey(Gimnasio, on_delete=models.CASCADE, related_name='resenas')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    estrellas = models.IntegerField(choices=[(i, str(i)) for i in range(6)])
    texto = models.TextField(max_length=500, blank=True, null=True, help_text="Reseña opcional (máximo 500 caracteres)")
    fecha = models.DateTimeField(auto_now_add=True)
    editado = models.BooleanField(default=False)
    fecha_edicion = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('usuario', 'gimnasio')

    def save(self, *args, **kwargs):
        # Si ya existe una reseña y se está actualizando, marcar como editado
        if self.pk:
            self.editado = True
            from django.utils import timezone
            self.fecha_edicion = timezone.now()
        
        # Guardar la reseña
        super().save(*args, **kwargs)

