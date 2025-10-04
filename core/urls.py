from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    RegistroUsuarioView, LoginView,
    GimnasioViewSet, RutinaViewSet, InventarioViewSet,
    MaquinaViewSet, FavoritoViewSet,ReseñaViewSet
)

router = DefaultRouter()
router.register(r'gimnasios', GimnasioViewSet)
router.register(r'rutinas', RutinaViewSet)
router.register(r'inventario', InventarioViewSet)
router.register(r'maquinas', MaquinaViewSet)
router.register(r'favoritos', FavoritoViewSet)
router.register(r'resenas', ReseñaViewSet)

urlpatterns = [
    # Vistas HTML
    path('', views.index, name='index'),
    path('login-page/', views.login_page, name='login'),  # página de login HTML
    path('register-page/', views.register_page, name='register'),  # página de registro HTML
    path('register-own/', views.register_page, name='register_own'),
    path('register/', views.post_reg, name='post_reg'), #formulario que solicita datos adicionales al usuario
    path('profile', views.profile, name= "profile"),
    path('smart-profile/', views.smart_profile, name='smart_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('eliminar-cuenta-usuario/', views.eliminar_cuenta_usuario, name='eliminar_cuenta_usuario'),
    path('login-usuario/', views.login_usuario, name='login_usuario'),
    path('verificar-email/<str:token>/', views.verificar_email, name='verificar_email'),
    path('reenviar-verificacion/', views.reenviar_verificacion, name='reenviar_verificacion'),
    path('search/', views.search, name= 'search'),
    path('logout/', views.logout_view, name='logout'),
    path('register-gym/', views.register_gym, name='reg_gym'),
    path('gym-profile/<int:gimnasio_id>/', views.gym_profile, name='gym_profile'),
    path('edit-gym-profile/<int:gimnasio_id>/', views.edit_gym_profile, name='edit_gym_profile'),
    path('edit-inventory/<int:gimnasio_id>/', views.edit_inventory, name='edit_inventory'),
    path('add-maquina/<int:gimnasio_id>/', views.add_maquina, name='add_maquina'),
    path('add-producto/<int:gimnasio_id>/', views.add_producto, name='add_producto'),
    path('delete-maquina/<int:gimnasio_id>/<int:maquina_id>/', views.delete_maquina, name='delete_maquina'),
    path('delete-producto/<int:gimnasio_id>/<int:producto_id>/', views.delete_producto, name='delete_producto'),
    path('edit-maquina/<int:gimnasio_id>/<int:maquina_id>/', views.edit_maquina, name='edit_maquina'),
    path('edit-producto/<int:gimnasio_id>/<int:producto_id>/', views.edit_producto, name='edit_producto'),
    path('delete-gym-account/<int:gimnasio_id>/', views.delete_gym_account, name='delete_gym_account'),
    path('gimnasio-resenas/<int:gimnasio_id>/', views.gimnasio_resenas, name='gimnasio_resenas'),
    path('editar-resena/<int:gimnasio_id>/<int:resena_id>/', views.editar_resena, name='editar_resena'),
    path('eliminar-resena/<int:gimnasio_id>/<int:resena_id>/', views.eliminar_resena, name='eliminar_resena'),
    path('buscar/', views.buscar_gimnasios, name='buscar_gimnasios'),
    path('api/gimnasio/<int:gimnasio_id>/detalle/', views.gimnasio_detalle_api, name='gimnasio_detalle_api'),

    # Endpoints API
    path('api/', include(router.urls)),
    path('api/registro/', RegistroUsuarioView.as_view(), name='api_registro'),
    path('api/login/', LoginView.as_view(), name='api_login'),
    path('api/', include(router.urls)),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
