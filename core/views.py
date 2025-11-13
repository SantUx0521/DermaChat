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
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage

def index(request):
    usuario = request.user 
    return render(request, 'core/index.html', {'usuario': usuario})



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

def register_page(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST.get('confirm_password')
        
        # Validamos que las contraseñas coincidan
        if password != confirm_password:
            return render(request, 'core/register.html', {'error': 'Las contraseñas no coinciden'})
        
        # Validamos que el correo no esté registrado
        if Usuario.objects.filter(email=email).exists():
            return render(request, 'core/register.html', {'error': 'Este correo electrónico ya está registrado'})
        
        
        usuario = Usuario.objects.create(
            email=email,
            nombre=nombre,
            password=make_password(password),
        )
        login(request, usuario)
        # Redirigir a selección de plan después del registro
        return redirect('select_plan')
    return render(request, 'core/register.html')

def login_usuario(request):
    if request.method == 'POST':
        data = json.loads(request.body) 
        email = data.get('email') 
        password = data.get('password')

        usuario = authenticate(request, username=email, password=password)

        if usuario is not None:
            login(request, usuario)
            return JsonResponse({'redirect': '/'} )     
        else:
            return JsonResponse({'error': 'correo y/o contraseña incorrecta'}, status=400)
    return render(request, 'core/login.html')


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
    if not request.user.is_authenticated:
        return redirect('login')
    usuario = request.user  # necesario para acceder directamente al usuario
    return render(request, 'core/profile.html', {'usuario': usuario})



def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
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
        
        # Redirigir con mensaje de éxito
        return redirect('profile')
    
    return render(request, 'core/edit_profile.html', {'usuario': usuario})
            

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
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=['post'])
    def enviar_mensaje(self, request, pk=None):
    
        conversacion = self.get_object()
        contenido = request.data.get('contenido')

        if not contenido:
            return Response({'error': 'El contenido no puede estar vacío.'}, status=status.HTTP_400_BAD_REQUEST)

        Mensaje.objects.create(
            conversacion=conversacion,
            remitente='usuario',
            contenido=contenido
        )

        # metodo para simular respuesta
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

def chat(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'GET' or request.method == 'POST':
        usuario = request.user  
        from django.conf import settings
        api_key = settings.VOICEFLOW_API_KEY
        print(f"DEBUG: API Key cargada: {api_key[:20] if api_key else 'VACÍA'}...")
        print(f"DEBUG: Longitud de API Key: {len(api_key) if api_key else 0}")
        context = {
            'usuario': usuario,
            'voiceflow_api_key': api_key or ''
        }
        return render(request, 'core/chat.html', context)
    
def recuperar_contraseña(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            usuario = Usuario.objects.get(email=email)
            token = secrets.token_urlsafe(32)
            usuario.token_recuperacion = token
            usuario.save()

            reset_link = f'http://{request.get_host()}/reestablecer/{token}/'
            send_mail(
                'Recupera tu contraseña en DermaChat',
                f'Por favor, restablece tu contraseña haciendo clic en el siguiente enlace:\n\n{reset_link}\n\n'
                f'Este enlace puede usarse una sola vez.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return render(request, 'core/olvidoContraseña.html', {
                'mensaje': 'Se ha enviado un email con el enlace para restablecer tu contraseña.'
            })
        except Usuario.DoesNotExist:
            return render(request, 'core/olvidoContraseña.html', {
                'error': 'No se encontró ninguna cuenta con este correo electrónico.'
            })

    return render(request, 'core/olvidoContraseña.html')

def restablecer_contraseña(request, token):
    try:
        usuario = Usuario.objects.get(token_recuperacion=token)
    except Usuario.DoesNotExist:
        return render(request, 'core/newPassword.html', {
            'error': 'El enlace de recuperación no es válido o ya fue usado.'
        })

    if request.method == 'POST':
        new_password = request.POST.get('nueva_contraseña')
        if len(new_password) >= 8:
            usuario.set_password(new_password)
            usuario.token_recuperacion = None
            usuario.save()
            return render(request, 'core/newPassword.html', {
                'mensaje': 'Tu contraseña ha sido restablecida con éxito.'
            })
        else:
            return render(request, 'core/newPassword.html', {
                'error': 'La contraseña debe tener al menos 8 caracteres.'
            })

    return render(request, 'core/newPassword.html', {'usuario': usuario})

def contacto(request):
    usuario = request.user 
    if request.method == 'POST':
        mensaje = request.POST.get('mensaje')
        if not mensaje.strip():
                return render(request, 'core/contact.html', {'error': 'El mensaje no puede estar vacío.'})
        asunto = "Nuevo mensaje de contacto"
        cuerpo = f"{mensaje}"

        try:
            send_mail(
                asunto,
                cuerpo,
                settings.DEFAULT_FROM_EMAIL,  
                ['chatderma481@gmail.com'],     
                fail_silently=False,
            )
            return redirect('contact_sent')
        except Exception as e:
            return render(request, 'core/contact.html', {'error': 'No se pudo enviar el mensaje.'})
    return render(request, 'core/contact.html', {'usuario': usuario})

def contacto_enviado(request):
    return render(request, 'core/contact_sent.html')

def select_plan(request):
    """Vista para seleccionar plan (Gratuito o Premium) después del registro o cambiar de plan"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        plan_choice = request.POST.get('plan')
        usuario = request.user
        
        if plan_choice == 'premium':
            # Si ya es premium, solo redirigir a index
            if usuario.es_premium:
                return redirect('profile')
            # Redirigir a opciones de pago
            return redirect('payment_options')
        elif plan_choice == 'free':
            # Usuario elige plan gratuito
            if usuario.es_premium:
                # Si tenía premium, cambiar a gratuito
                usuario.es_premium = False
                usuario.save()
            # Continuar al index
            return redirect('profile')
    
    usuario = request.user
    return render(request, 'core/select_plan.html', {'usuario': usuario})

def payment_options(request):
    """Vista para mostrar opciones de pago y beneficios del plan Premium"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        # Aquí iría la lógica de procesamiento de pago
        # Por ahora, solo marcamos al usuario como premium
        payment_plan = request.POST.get('payment_plan')
        
        if payment_plan:
            # En una implementación real, aquí se procesaría el pago
            # Por ahora, marcamos al usuario como premium
            usuario = request.user
            usuario.es_premium = True
            usuario.save()
            return redirect('index')
    
    usuario = request.user
    context = {
        'usuario': usuario,
        'premium_benefits': [
            'Análisis ilimitado de imágenes',
            'Prioridad en el análisis',
            'Acceso a reportes detallados',
            'Soporte prioritario',
            'Sin límites de uso diario',
            'Historial completo de análisis'
        ]
    }
    return render(request, 'core/payment_options.html', context)

def analyze_image(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)

    if request.method != 'POST' or 'image' not in request.FILES:
        return JsonResponse({'error': 'No se recibió imagen'}, status=400)

    image_file = request.FILES['image']
    fs = FileSystemStorage()
    filename = fs.save(image_file.name, image_file)
    image_url = fs.url(filename)
    image_path = fs.path(filename)

    # =============================================
    # AQUÍ IRÁ TU MODELO DE IA (por ahora simulamos)
    # =============================================
    # Ejemplo futuro:
    # description = analizar_con_modelo(image_path)

    # Aqui se debe colocar el analisis de imagen
    respuestas_posibles = [
        "texto placeholder"
    ]
    
    import random
    description = random.choice(respuestas_posibles)

    # =============================================

    # Respuesta del bot con imagen + análisis real
    bot_html = f'''
    <div style="text-align:left; margin:15px 0;">
        <img src="{image_url}" style="max-width:280px; width:100%; border-radius:16px; 
             box-shadow:0 6px 20px rgba(0,0,0,0.2); display:block; margin-bottom:12px;">
        <div style="background:#e3f2fd; padding:14px 18px; border-radius:18px; 
             display:inline-block; max-width:92%; border-left:4px solid #1976d2;">
            <p style="margin:0; color:#1565c0; font-size:15px; line-height:1.5;">
                <strong>Análisis preliminar:</strong><br>{description}
            </p>
        </div>
    </div>
    '''

    return JsonResponse({'html': bot_html})