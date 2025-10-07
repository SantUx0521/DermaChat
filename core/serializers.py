from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from .models import Usuario, Conversacion, Mensaje


# ------------------------
# USUARIO SERIALIZER
# ------------------------
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id','email','nombre','password','edad','foto_perfil','email_verificado','es_premium',]
        extra_kwargs = {
            'password': {'write_only': True},
            'email_verificado': {'read_only': True},
        }

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        usuario = Usuario.objects.create(**validated_data)

        # Envío de correo opcional (si usas SMTP configurado)
        send_mail(
            'Confirmación de Registro',
            'Gracias por registrarte en DermaChat.',
            'DermaChat <noreply@dermachat.com>',
            [usuario.email],
            fail_silently=True,
        )
        return usuario


# ------------------------
# MENSAJE SERIALIZER
# ------------------------
class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = ['id','remitente','contenido','creado_en',]
        read_only_fields = ['id', 'creado_en']


# ------------------------
# CONVERSACION SERIALIZER
# ------------------------
class ConversacionSerializer(serializers.ModelSerializer):
    mensajes = MensajeSerializer(many=True, read_only=True)
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Conversacion
        fields = ['id','usuario','titulo','creada_en','mensajes',]
        read_only_fields = ['id', 'creada_en', 'mensajes']

    def create(self, validated_data):
        # Asignar usuario desde la vista (request.user)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['usuario'] = request.user
        return super().create(validated_data)
