from itertools import count
import json
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
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
import mercadopago
from rest_framework.decorators import api_view
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


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

def select_plan(request):
    """Vista para seleccionar plan (Gratuito o Premium) después del registro o cambiar de plan"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        plan_choice = request.POST.get('plan')
        usuario = request.user

        if plan_choice == 'premium':
            if usuario.es_premium:
                return redirect('profile')
            return redirect('payment_options')
        elif plan_choice == 'free':
            if usuario.es_premium:
                usuario.es_premium = False
                usuario.save()

            return redirect('profile')
    
    usuario = request.user
    return render(request, 'core/select_plan.html', {'usuario': usuario})

def payment_options(request):
    if not request.user.is_authenticated:
        return redirect('login')

    usuario = request.user

    if request.method == 'POST':
        payment_plan = request.POST.get('payment_plan')

        if payment_plan:
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

            success_url = request.build_absolute_uri(reverse("payment_success"))
            failure_url = request.build_absolute_uri(reverse("payment_failure"))
            pending_url = request.build_absolute_uri(reverse("payment_pending"))

            preference_data = {
                "items": [
                    {
                        "title": "Suscripción Premium DermaChat",
                        "quantity": 1,
                        "currency_id": "COP",
                        "unit_price": 1,
                    }
                ],
                "payer": {
                    "email": usuario.email,
                },
                "back_urls": {
                    "success": success_url,
                    "failure": failure_url,
                    "pending": pending_url,
                },
                "auto_return": "approved",
            }

            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]

            init_point = preference.get("init_point") or preference.get("sandbox_init_point")
            if not init_point:
                print("⚠️ Mercado Pago no devolvió URL de pago:", preference)
                return JsonResponse({"error": "Mercado Pago no devolvio URL de pago"}, status=500)

            return redirect(init_point)

    context = {
        "usuario": usuario,
        "premium_benefits": [
            "Análisis ilimitado de imágenes",
            "Prioridad en el análisis",
            "Acceso a reportes detallados",
            "Soporte prioritario",
            "Sin límites de uso diario",
            "Historial completo de análisis",
        ],
    }
    return render(request, "core/payment_options.html", context)

def payment_success(request):
    user = request.user
    if user.is_authenticated:
        user.es_premium = True
        user.save()
    return render(request, 'core/payment_success.html')

def payment_failure(request):
    return render(request, 'core/payment_failure.html')

def payment_pending(request):
    return render(request, 'core/payment_pending.html')

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

    from django.conf import settings
    import requests
    import os
    
    analysis_result = None
    severity = None
    detected_features = []
    
    try:
        # Llamar a la API de Roboflow
        roboflow_api_key = getattr(settings, 'ROBOFLOW_API_KEY', '')
        roboflow_model_id = getattr(settings, 'ROBOFLOW_MODEL_ID', '')
        roboflow_version = getattr(settings, 'ROBOFLOW_VERSION', '1')
        
        if roboflow_api_key and roboflow_model_id:
            if '/' in roboflow_model_id:
                roboflow_url = f"https://detect.roboflow.com/{roboflow_model_id}?api_key={roboflow_api_key}"
            else:
                # Solo model_id, agregar version
                roboflow_url = f"https://detect.roboflow.com/{roboflow_model_id}/{roboflow_version}?api_key={roboflow_api_key}"
            
            print(f"DEBUG: Llamando a Roboflow")
            print(f"DEBUG: URL: {roboflow_url}")
            print(f"DEBUG: Model ID: {roboflow_model_id}")
            print(f"DEBUG: Version: {roboflow_version}")
            print(f"DEBUG: API Key (primeros 10 chars): {roboflow_api_key[:10]}...")
            print(f"DEBUG: Ruta de imagen: {image_path}")
            print(f"DEBUG: Tamaño de imagen: {os.path.getsize(image_path)} bytes")
            
            # Enviar la imagen a Roboflow
            # Roboflow acepta imágenes como base64 o como archivo
            try:
                import base64
                
                # Leer la imagen y codificarla en base64
                with open(image_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                
                # Roboflow acepta base64 en el body
                # La URL ya incluye api_key como parámetro
                response = requests.post(
                    roboflow_url,
                    data=img_data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    timeout=30
                )
                
                # Si falla con base64, intentar con file upload (sin api_key en params porque ya está en URL)
                if response.status_code != 200:
                    print(f"DEBUG: Intento con base64 falló ({response.status_code}): {response.text[:200]}")
                    print(f"DEBUG: Intentando con file upload...")
                    with open(image_path, 'rb') as img_file:
                        files = {'file': (os.path.basename(image_path), img_file, 'image/jpeg')}
                        response = requests.post(
                            roboflow_url,
                            files=files,
                            timeout=30
                        )
                
                print(f"DEBUG: Respuesta de Roboflow - Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        predictions = response.json()
                    except Exception as e:
                        print(f"ERROR: No se pudo parsear JSON de Roboflow: {e}")
                        print(f"DEBUG: Respuesta raw: {response.text[:500]}")
                        raise
                    
                    print(f"DEBUG: Predicciones de Roboflow (completo): {json.dumps(predictions, indent=2)}")
                    
                    # Procesar las predicciones de Roboflow
                    # Roboflow puede devolver diferentes formatos según el tipo de modelo
                    detections = []
                    
                    # Intentar diferentes estructuras de respuesta
                    if 'predictions' in predictions:
                        detections = predictions['predictions']
                    elif 'detections' in predictions:
                        detections = predictions['detections']
                    elif isinstance(predictions, list):
                        detections = predictions
                    elif 'results' in predictions:
                        detections = predictions['results']
                    
                    print(f"DEBUG: Número de detecciones encontradas: {len(detections)}")
                    print(f"DEBUG: Estructura de la primera detección (si existe): {detections[0] if detections else 'N/A'}")
                    
                    # Contar detecciones por tipo
                    acne_count = 0
                    red_pimple_count = 0
                    blackhead_count = 0
                    dark_spot_count = 0
                    nodules_count = 0
                    papules_count = 0
                    pustules_count = 0
                    whitehead_count = 0
                    
                    for detection in detections:
                        # Roboflow puede devolver diferentes estructuras
                        class_name = ''
                        confidence = 0
                        
                        if isinstance(detection, dict):
                            class_name = detection.get('class', detection.get('name', '')).lower()
                            confidence = detection.get('confidence', detection.get('score', 0))
                        elif isinstance(detection, str):
                            class_name = detection.lower()
                            confidence = 1.0
                        
                        print(f"DEBUG: Detección - Clase: {class_name}, Confianza: {confidence}")
                        
                        if confidence > 0.5:  # Solo considerar detecciones con confianza > 50%
                            normalized_class = class_name.replace('-', ' ').replace('_', ' ')
                            if any(keyword in normalized_class for keyword in ['acne', 'acné', 'pimple', 'granito', 'zit']):
                                if any(keyword in normalized_class for keyword in ['red', 'rojo', 'rojizo', 'inflamed']):
                                    red_pimple_count += 1
                                else:
                                    acne_count += 1
                            elif any(keyword in normalized_class for keyword in ['papule', 'pápula']):
                                papules_count += 1
                            elif any(keyword in normalized_class for keyword in ['pustule', 'pústula']):
                                pustules_count += 1
                            elif any(keyword in normalized_class for keyword in ['blackhead', 'punto negro', 'comedón', 'comedon']):
                                blackhead_count += 1
                            elif any(keyword in normalized_class for keyword in ['whitehead', 'punto blanco']):
                                whitehead_count += 1
                            elif any(keyword in normalized_class for keyword in ['dark spot', 'mancha oscura', 'spot', 'lesion', 'lesión', 'stain']):
                                dark_spot_count += 1
                            elif any(keyword in normalized_class for keyword in ['nodule', 'nódulo', 'quiste', 'cyst']):
                                nodules_count += 1
                            # Si la clase es directamente "leve", "moderado", "grave"
                            elif class_name in ['leve', 'moderado', 'grave', 'severo', 'severe']:
                                severity = class_name if class_name != 'severo' else 'grave'
                                detected_features = [f"Clasificación directa: {severity}"]
                                analysis_result = f"Severidad: {severity}. Clasificación directa del modelo."
                                print(f"DEBUG: Severidad directa detectada en la clase: {severity}")
                                break
                    
                    # Determinar severidad basada en el número de detecciones
                    total_detections = (
                        acne_count
                        + blackhead_count
                        + red_pimple_count
                        + dark_spot_count
                        + nodules_count
                        + papules_count
                        + pustules_count
                        + whitehead_count
                    )
                    print(
                        "DEBUG: Total detecciones - "
                        f"Lesiones generales: {acne_count}, "
                        f"Puntos negros: {blackhead_count}, "
                        f"Granos rojos: {red_pimple_count}, "
                        f"Dark spots: {dark_spot_count}, "
                        f"Nódulos: {nodules_count}, "
                        f"Pápulas: {papules_count}, "
                        f"Pústulas: {pustules_count}, "
                        f"Puntos blancos: {whitehead_count}, "
                        f"Total: {total_detections}"
                    )
                    
                    # Verificar si Roboflow devolvió una clasificación directa de severidad
                    severity_direct = None
                    if 'severity' in predictions:
                        severity_direct = predictions.get('severity')
                    elif 'classification' in predictions:
                        severity_direct = predictions.get('classification')
                    
                    if severity_direct:
                        severity = str(severity_direct).lower()
                        if severity not in ['leve', 'moderado', 'grave', 'severo']:
                            if severity in ['mild', 'light', 'leve']:
                                severity = "leve"
                            elif severity in ['moderate', 'moderado']:
                                severity = "moderado"
                            elif severity in ['severe', 'grave', 'severo']:
                                severity = "grave"
                            else:
                                severity = "moderado"  # Default si no reconocemos el valor
                        print(f"DEBUG: Severidad directa del modelo: {severity}")
                    elif total_detections == 0:
                        severity = "leve"
                    elif total_detections < 5:
                        severity = "leve"
                    elif total_detections < 15:
                        severity = "moderado"
                    else:
                        severity = "grave"
                    
                    # Construir descripción de características detectadas
                    features = []
                    if blackhead_count > 0:
                        features.append(f"{blackhead_count} punto(s) negro(s)")
                    if red_pimple_count > 0:
                        features.append(f"{red_pimple_count} grano(s) rojizo(s)")
                    if acne_count > 0:
                        features.append(f"{acne_count} lesión(es) de acné")
                    if dark_spot_count > 0:
                        features.append(f"{dark_spot_count} mancha(s) oscura(s)")
                    if papules_count > 0:
                        features.append(f"{papules_count} pápula(s)")
                    if pustules_count > 0:
                        features.append(f"{pustules_count} pústula(s)")
                    if whitehead_count > 0:
                        features.append(f"{whitehead_count} punto(s) blanco(s)")
                    if nodules_count > 0:
                        features.append(f"{nodules_count} nódulo(s)/quiste(s)")
                    
                    detected_features = features
                    
                    # Crear el texto de análisis para Voiceflow
                    if features:
                        analysis_text = f"Severidad: {severity}. Se detectaron: {', '.join(features)}."
                    else:
                        analysis_text = f"Severidad: {severity}. No se detectaron características específicas."
                    
                    analysis_result = analysis_text
                    print(f"DEBUG: Análisis final - Severidad: {severity}, Características: {features}")
                    
                else:
                    # Si falla Roboflow, mostrar el error y usar fallback
                    error_text = response.text
                    print(f"ERROR: Roboflow devolvió status {response.status_code}: {error_text}")
                    # Usar el procesador local como fallback
                    try:
                        import sys
                        sys.path.append(os.path.join(settings.BASE_DIR, 'ChatBot-IA'))
                        severity = determine(image_path)
                        analysis_result = f"Severidad: {severity} (análisis local - Roboflow falló)"
                        print(f"DEBUG: Usando análisis local - Severidad: {severity}")
                    except Exception as e:
                        print(f"Error en análisis local: {e}")
                        severity = "moderado"
                        analysis_result = "No se pudo realizar un análisis detallado, pero se detectó actividad en la piel."
            except requests.exceptions.RequestException as e:
                print(f"ERROR: Excepción al llamar a Roboflow: {e}")
                # Usar fallback
                try:
                    import sys
                    sys.path.append(os.path.join(settings.BASE_DIR, 'ChatBot-IA'))
                    severity = determine(image_path)
                    analysis_result = f"Severidad: {severity} (análisis local - Error de conexión)"
                except Exception as e2:
                    print(f"Error en análisis local: {e2}")
                    severity = "moderado"
                    analysis_result = "No se pudo realizar un análisis detallado, pero se detectó actividad en la piel."
        else:
            # Si no hay configuración de Roboflow, usar procesador local
            try:
                import sys
                sys.path.append(os.path.join(settings.BASE_DIR, 'ChatBot-IA'))
                severity = determine(image_path)
                analysis_result = f"Severidad: {severity} (análisis local)"
            except Exception as e:
                print(f"Error en análisis local: {e}")
                severity = "moderado"
                analysis_result = "Análisis básico: se detectó actividad en la piel."
                
    except Exception as e:
        print(f"Error al analizar imagen: {e}")
        severity = "moderado"
        analysis_result = "Hubo un problema al analizar la imagen, pero puedo ayudarte con recomendaciones generales."

    if detected_features:
        description = f"Severidad: <strong>{severity}</strong><br>Características detectadas: {', '.join(detected_features)}"
    else:
        description = f"Severidad: <strong>{severity}</strong>"

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

    return JsonResponse({
        'html': bot_html,
        'analysis_result': analysis_result,
        'severity': severity,
        'detected_features': detected_features
    })

# ============ Historial ==================
def historial(request):
    if not request.user.is_authenticated:
        return redirect('login')  

    usuario = request.user
    conversaciones = Conversacion.objects.filter(usuario=usuario).order_by('-creada_en')
    
    # Si se proporciona un ID de conversación 
    conversacion_id = request.GET.get('conversacion_id')
    mensajes = None
    conversacion_seleccionada = None
    if conversacion_id:
        conversacion_seleccionada = get_object_or_404(Conversacion, id=conversacion_id, usuario=usuario)
        mensajes = Mensaje.objects.filter(conversacion=conversacion_seleccionada).order_by('creado_en')

    context = {
        'usuario': usuario,
        'conversaciones': conversaciones,
        'conversacion_seleccionada': conversacion_seleccionada,
        'mensajes': mensajes,
    }
    return render(request, 'core/historial.html', context)

# ============ guardar conversaciones ============

@csrf_exempt  # ← Esto ahora SÍ funciona porque es una vista normal
def guardar_mensaje(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "No autenticado"}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    texto_usuario = data.get('mensaje_usuario', '').strip()
    texto_bot = data.get('mensaje_bot', '').strip()
    conversacion_id = data.get('conversacion_id')

    # Crear o recuperar conversación
    if conversacion_id:
        try:
            conversacion = Conversacion.objects.get(id=conversacion_id, usuario=request.user)
        except Conversacion.DoesNotExist:
            conversacion = Conversacion.objects.create(usuario=request.user, titulo="Nueva conversación")
    else:
        titulo = texto_usuario[:60] if texto_usuario else "Chat nuevo"
        conversacion = Conversacion.objects.create(usuario=request.user, titulo=titulo)

    # Guardar mensajes
    if texto_usuario:
        Mensaje.objects.create(conversacion=conversacion, remitente='usuario', contenido=texto_usuario)
    if texto_bot:
        Mensaje.objects.create(conversacion=conversacion, remitente='ia', contenido=texto_bot)

    return JsonResponse({"conversacion_id": conversacion.id})

# ============ recuperar las conversaciones para el chat============
@api_view(['GET'])
def obtener_mensajes_conversacion(request, conversacion_id):
    if not request.user.is_authenticated:
        return Response({"error": "No autenticado"}, status=401)
    
    try:
        conversacion = Conversacion.objects.get(id=conversacion_id, usuario=request.user)
        mensajes = conversacion.mensajes.all().order_by('creado_en')
        data = [{
            "remitente": msg.remitente,
            "contenido": msg.contenido,
            "hora": msg.creado_en.strftime("%H:%M")
        } for msg in mensajes]
        return Response(data)
    except Conversacion.DoesNotExist:
        return Response({"error": "Conversación no encontrada"}, status=404)