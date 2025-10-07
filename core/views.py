from itertools import count
import json
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from .models import *
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import login
#verificacion de email
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import secrets
from datetime import timedelta
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import logout
from django.db.models import Count, Avg
from rest_framework.exceptions import PermissionDenied
from .models import  Conversacion, Mensaje ,Usuario
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

def index(request):
    return render(request, 'core/index.html')
    
# ----------------------------
# buscar un gimnasio por nombre
# ----------------------------



# ----------------------------
# Registro de usuario
# ----------------------------
class RegistroUsuarioView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.AllowAny]


# ----------------------------
# Login (Token)
# ----------------------------
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        if request.method == 'POST':
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            usuario = authenticate(request, username=email, password=password)

            if usuario is not None:
                # Verificar si el correo está verificado
                if not usuario.email_verificado:
                    return JsonResponse({'error': 'Debes verificar tu correo electrónico antes de iniciar sesión. Revisa tu bandeja de entrada.'}, status=400)
                
                login(request, usuario)
                return JsonResponse({'mensaje': 'Inicio de sesión exitoso'})
            else:
                return JsonResponse({'error': 'correo y/o contraseña incorrecta'}, status=400)
    
    

#----------------------------
# Login (HTML)
# ---------------------------    
def login_page(request):
    return render(request, 'core/login.html')

@ensure_csrf_cookie
def register_page(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo_usuario')
        nombre = request.POST['nombre']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST.get('confirm_password')
        
        # Validar que las contraseñas coincidan
        if password != confirm_password:
            return render(request, 'core/register.html', {'error': 'Las contraseñas no coinciden'})
        
        # Validar que el correo no esté registrado
        if Usuario.objects.filter(email=email).exists():
            return render(request, 'core/register.html', {'error': 'Este correo electrónico ya está registrado'})
        
        # Generar token de verificación
        token = secrets.token_urlsafe(32)
        fecha_expiracion = timezone.now() + timedelta(hours=24)
        
        usuario = Usuario.objects.create(
            nombre=nombre,
            email=email,
            password=make_password(password),
            token_verificacion=token,
            fecha_token=fecha_expiracion,
            es_dueño=(tipo == 'dueño')
        )
        
        # Enviar email de verificación
        send_mail(
            'Verifica tu cuenta en GMSearch',
            f'Por favor, verifica tu cuenta haciendo clic en el siguiente enlace:\n\n'
            f'http://{request.get_host()}/verificar-email/{token}/\n\n'
            f'Este enlace expirará en 24 horas.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        return render(request, 'core/verificacion_pendiente.html')
    if 'register-own' in request.path: #en caso de que el registro venga por parte de un dueño de gimnasio toma los datos del html correspondiente
        return render(request, 'core/registerOwn.html')
    return render(request, 'core/register.html')





def verificar_email(request, token):
    try:
        usuario = Usuario.objects.get(token_verificacion=token)
        if usuario.fecha_token and usuario.fecha_token > timezone.now():
            usuario.email_verificado = True
            usuario.is_active = True
            usuario.token_verificacion = None
            usuario.fecha_token = None
            usuario.save()
            
            # Redirigir a la página de login con mensaje de éxito
            context = {
                'es_dueño': usuario.es_dueño,
                'nombre_usuario': usuario.nombre
            }
            return render(request, 'core/verificacion_exitosa.html', context)
        else:
            return render(request, 'core/token_expirado.html')
    except Usuario.DoesNotExist:
        return render(request, 'core/token_invalido.html')



def post_reg(request):
    if request.method == 'POST': # utilizado para añadir datos adicionales sobre el usuario, que se veran desplegados en su profile
        usuario = request.user
        usuario.nombres = request.POST.get('nombres')
        usuario.edad = request.POST.get('edad') or None
        usuario.save()
        return redirect('profile')
    
    # Obtener datos de la sesión
    context = {
        'nombre_usuario': request.session.get('nombre_usuario', ''),
        'email_usuario': request.session.get('email_usuario', '')
    }
    return render(request, 'core/PostRegister.html', context)

def profile(request):
    usuario = request.user  # necesario para acceder directamente al usuario
    return render(request, 'core/profile.html', {'usuario': usuario})



def edit_profile(request):
    usuario = request.user
    
    if request.method == 'POST':
        print("DEBUG: Método POST recibido")
        print("DEBUG: FILES disponibles:", request.FILES.keys())
        
        # Actualizar los datos del usuario
        usuario.nombre = request.POST.get('nombre', usuario.nombre)
        usuario.email = request.POST.get('email', usuario.email)
        usuario.edad = request.POST.get('edad') or None
        
        
        # Manejar la subida de la foto de perfil
        if 'foto_perfil' in request.FILES:
            print("DEBUG: Foto de perfil encontrada en FILES")
            usuario.foto_perfil = request.FILES['foto_perfil']
            print("DEBUG: Foto asignada:", usuario.foto_perfil)
        else:
            print("DEBUG: No se encontró foto_perfil en FILES")
        
        # Manejar cambio de contraseña
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if current_password and new_password and confirm_password:
            # Verificar que la contraseña actual sea correcta
            if usuario.check_password(current_password):
                # Verificar que las nuevas contraseñas coincidan
                if new_password == confirm_password:
                    # Verificar que la nueva contraseña tenga al menos 8 caracteres
                    if len(new_password) >= 8:
                        usuario.set_password(new_password)
                        print("DEBUG: Contraseña cambiada exitosamente")
                    else:
                        print("DEBUG: Nueva contraseña muy corta")
                        return render(request, 'core/edit_profile.html', {
                            'usuario': usuario, 
                            'error': 'La nueva contraseña debe tener al menos 8 caracteres'
                        })
                else:
                    print("DEBUG: Las contraseñas no coinciden")
                    return render(request, 'core/edit_profile.html', {
                        'usuario': usuario, 
                        'error': 'Las nuevas contraseñas no coinciden'
                    })
            else:
                print("DEBUG: Contraseña actual incorrecta")
                return render(request, 'core/edit_profile.html', {
                    'usuario': usuario, 
                    'error': 'La contraseña actual es incorrecta'
                })
        
        # Guardar los cambios
        usuario.save()
        print("DEBUG: Usuario guardado. Foto actual:", usuario.foto_perfil)
        
        return redirect('profile')
    
    return render(request, 'core/edit_profile.html', {'usuario': usuario})
    
def login_usuario(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        usuario = authenticate(request, username=email, password=password)

        if usuario is not None:
            # Verificar si el correo está verificado
            if not usuario.email_verificado:
                return JsonResponse({'error': 'Debes verificar tu correo electrónico antes de iniciar sesión. Revisa tu bandeja de entrada.'}, status=400)
            
            login(request, usuario)
            

def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('index')






def reenviar_verificacion(request):
    """Vista para reenviar el email de verificación"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            usuario = Usuario.objects.get(email=email)
            if not usuario.email_verificado:
                # Generar nuevo token de verificación
                token = secrets.token_urlsafe(32)
                fecha_expiracion = timezone.now() + timedelta(hours=24)
                
                usuario.token_verificacion = token
                usuario.fecha_token = fecha_expiracion
                usuario.save()
                
                # Enviar email de verificación
                send_mail(
                    'Verifica tu cuenta en GMSearch',
                    f'Por favor, verifica tu cuenta haciendo clic en el siguiente enlace:\n\n'
                    f'http://{request.get_host()}/verificar-email/{token}/\n\n'
                    f'Este enlace expirará en 24 horas.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                return render(request, 'core/verificacion_pendiente.html', {
                    'mensaje': 'Se ha reenviado el email de verificación. Revisa tu bandeja de entrada.'
                })
            else:
                return render(request, 'core/verificacion_pendiente.html', {
                    'error': 'Este correo ya está verificado.'
                })
        except Usuario.DoesNotExist:
            return render(request, 'core/verificacion_pendiente.html', {
                'error': 'No se encontró una cuenta con este correo electrónico.'
            })
    
    return render(request, 'core/reenviar_verificacion.html')

def eliminar_cuenta_usuario(request):
    """Vista para eliminar la cuenta del usuario"""
    if request.method == 'POST':
        try:
            # Eliminar el usuario (esto también eliminará todas las relaciones)
            usuario = request.user
            usuario.delete()
            # Cerrar sesión
            logout(request)
            return redirect('index')
        except Exception as e:
            # En caso de error, redirigir al perfil
            return redirect('profile')
    
    return redirect('profile')

class ConversacionViewSet(viewsets.ModelViewSet):
    serializer_class = ConversacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['titulo']

    def get_queryset(self):
        #filtro para que cada usuario sea el unico en ver sus comveraciones
        return Conversacion.objects.filter(usuario=self.request.user).order_by('-creada_en')

    def perform_create(self, serializer):
        # metodo para asignar automaticamente al usuario
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=['post'])
    def enviar_mensaje(self, request, pk=None):
    
        conversacion = self.get_object()
        contenido = request.data.get('contenido')

        if not contenido:
            return Response({'error': 'El contenido no puede estar vacío.'}, status=status.HTTP_400_BAD_REQUEST)

        # guardar un mensaje del usuario
        Mensaje.objects.create(
            conversacion=conversacion,
            remitente='usuario',
            contenido=contenido
        )

        # metodo provicional para simular respuesta
        #aqui se debe añadir la APi de la IA
        respuesta = f"Hola {request.user.nombre}, recibí tu mensaje: '{contenido}'"
        Mensaje.objects.create(
            conversacion=conversacion,
            remitente='ia',
            contenido=respuesta
        )

        # metodo para devolver la conversación actualizada
        serializer = self.get_serializer(conversacion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MensajeViewSet(viewsets.ModelViewSet):

    serializer_class = MensajeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Mensaje.objects.filter(
            conversacion__usuario=self.request.user
        ).order_by('creado_en')

    def perform_create(self, serializer):
        conversacion_id = self.request.data.get('conversacion')
        conversacion = get_object_or_404(Conversacion, id=conversacion_id, usuario=self.request.user)

        serializer.save(conversacion=conversacion)