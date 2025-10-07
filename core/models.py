from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models import Avg
from django.conf import settings

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
    foto_perfil = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    email_verificado = models.BooleanField(default=False)
    es_premium = models.BooleanField(default=False)
    token_verificacion = models.CharField(max_length=100, blank=True, null=True)
    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']
    
    def __str__(self):
        return self.email
        
class Conversacion(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversaciones'
    )
    titulo = models.CharField(max_length=255, blank=True, null=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo or f"Chat de {self.usuario.nombre} ({self.creada_en.strftime('%Y-%m-%d %H:%M')})"


class Mensaje(models.Model):
    conversacion = models.ForeignKey(
        Conversacion,
        on_delete=models.CASCADE,
        related_name='mensajes'
    )
    remitente = models.CharField(
        max_length=10,
        choices=[('usuario', 'Usuario'), ('ia', 'IA')]
    )
    contenido = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.remitente.upper()} ({self.creado_en:%H:%M}): {self.contenido[:40]}"