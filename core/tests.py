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
        password=make_password("passwordseguro")
    )


@pytest.mark.django_db
def test_registro_usuario_email_duplicado(usuario_existente):
    client = APIClient()
    payload = {
        "email": "existente@example.com",  # Mismo email que la fixture
        "nombre": "Otro Nombre",
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
        password=make_password("password123")  # encriptación manual
    )

    payload = {
        "email": "duplicado@example.com",
        "nombre": "Nuevo Nombre",
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


