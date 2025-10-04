import pytest
from django.test import TestCase
from rest_framework.test import APIClient,APITestCase
from core.models import Usuario
from .models import Usuario, Gimnasio, Maquina, FichaBiometrica, ClienteGimnasio, Favorito
from django.db.utils import IntegrityError
from core.models import Usuario
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework import status

@pytest.fixture
def usuario_existente(db):
    return Usuario.objects.create(
        email="existente@example.com",
        nombre="Usuario Existente",
        direccion="Calle Real 456",
        telefono="987654321",
        es_dueño=False,
        password=make_password("passwordseguro")
    )


@pytest.mark.django_db
def test_registro_usuario_email_duplicado(usuario_existente):
    client = APIClient()
    payload = {
        "email": "existente@example.com",  # Mismo email que la fixture
        "nombre": "Otro Nombre",
        "direccion": "Otra Dirección",
        "telefono": "111111111",
        "es_dueño": False,
        "password": "otra_pass"
    }

    response = client.post("/api/registro/", payload)  # Usa el endpoint real
    assert response.status_code == 400
    assert "email" in str(response.data).lower()

@pytest.mark.django_db
def test_registro_usuario_email_duplicado():
    client = APIClient()
    Usuario.objects.create(
        email="duplicado@example.com",
        nombre="Usuario Duplicado",
        direccion="Calle 1",
        telefono="000000000",
        es_dueño=False,
        password=make_password("password123")  # encriptación manual
    )

    payload = {
        "email": "duplicado@example.com",
        "nombre": "Nuevo Nombre",
        "direccion": "Nueva Dirección",
        "telefono": "111111111",
        "es_dueño": False,
        "password": "otra_pass"
    }

    response = client.post("/api/registro/", payload)
    assert response.status_code == 400
    assert "email" in str(response.data).lower()


class UsuarioModelTest(TestCase):

    def test_crear_usuario(self):
        user = Usuario.objects.create_user(
            email='prueba@example.com',
            nombre='Juan Pérez',
            password='password123'
        )
        self.assertEqual(user.email, 'prueba@example.com')
        self.assertTrue(user.check_password('password123'))
        self.assertFalse(user.is_staff)

    def test_crear_superusuario(self):
        admin = Usuario.objects.create_superuser(
            email='admin@example.com',
            nombre='Admin User',
            password='adminpass'
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)




class FichaBiometricaModelTest(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create_user(
            email='ficha@example.com', nombre='Ficha User', password='pass'
        )

    def test_crear_ficha_biometrica(self):
        ficha = FichaBiometrica.objects.create(
            usuario=self.user, altura=1.75, peso=70.5
        )
        self.assertEqual(ficha.altura, 1.75)
        self.assertEqual(ficha.usuario.email, 'ficha@example.com')


class GimnasioModelTest(TestCase):

    def setUp(self):
        self.owner = Usuario.objects.create_user(
            email='dueno@example.com', nombre='Dueño', password='pass'
        )

    def test_crear_gimnasio(self):
        gym = Gimnasio.objects.create(
            dueño=self.owner,
            nombre_gym='Gym Test',
            ubicacion='Ciudad',
            precio_inscripcion=100.00,
            descripcion='Un gimnasio de prueba',
        )
        self.assertEqual(gym.nombre_gym, 'Gym Test')
        self.assertEqual(gym.dueño.email, 'dueno@example.com')



class ClienteGimnasioModelTest(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create_user(
            email='cliente@example.com', nombre='Cliente', password='pass'
        )
        self.gym = Gimnasio.objects.create(
            dueño=self.user,
            nombre_gym='Gym Test',
            ubicacion='Ciudad',
            precio_inscripcion=50.00,
            descripcion='Gym Test Desc',
        )

    def test_cliente_inscripcion_unica(self):
        ClienteGimnasio.objects.create(usuario=self.user, gimnasio=self.gym)
        with self.assertRaises(IntegrityError):
            ClienteGimnasio.objects.create(usuario=self.user, gimnasio=self.gym)


class FavoritoModelTest(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create_user(
            email='fav@example.com', nombre='Favorito', password='pass'
        )
        self.gym = Gimnasio.objects.create(
            dueño=self.user,
            nombre_gym='Gym Fav',
            ubicacion='Ciudad',
            precio_inscripcion=80.00,
            descripcion='Desc',
        )

    def test_favorito_unico(self):
        Favorito.objects.create(usuario=self.user, gimnasio=self.gym)
        with self.assertRaises(IntegrityError):
            Favorito.objects.create(usuario=self.user, gimnasio=self.gym)


