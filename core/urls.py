from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    RegistroUsuarioView, LoginView,ConversacionViewSet,MensajeViewSet,
)

router = DefaultRouter()
router.register(r'conversaciones', ConversacionViewSet, basename='conversacion')
router.register(r'mensajes', MensajeViewSet, basename='mensaje')

urlpatterns = [
    path('', views.index, name='index'),
    path('login-page/', views.login_page, name='login'),  # página de login HTML
    path('register-page/', views.register_page, name='register'),  # página de registro HTML
    path('register-own/', views.register_page, name='register_own'),
    path('register/', views.post_reg, name='post_reg'), #formulario que solicita datos adicionales al usuario
    path('profile', views.profile, name= "profile"),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('eliminar-cuenta-usuario/', views.eliminar_cuenta_usuario, name='eliminar_cuenta_usuario'),
    path('login-usuario/', views.login_usuario, name='login_usuario'),
    path('recuperar/', views.recuperar_contraseña, name='recuperar'),
    path('reestablecer/<str:token>/', views.restablecer_contraseña, name='restablecer'),
    path('logout/', views.logout_view, name='logout'),

    path('verificar-email/<str:token>/', views.verificar_email, name='verificar_email'),
    path('reenviar-verificacion/', views.reenviar_verificacion, name='reenviar_verificacion'),
    path('chat/', views.chat, name='chat'),

    path('api/', include(router.urls)),
    path('api/registro/', RegistroUsuarioView.as_view(), name='api_registro'),
    path('api/login/', LoginView.as_view(), name='api_login'),
    path('api/', include(router.urls)),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
