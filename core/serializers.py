from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from .models import (
    Usuario, Gimnasio, FichaBiometrica, ClienteGimnasio, Favorito,
    Rutina, Maquina, Inventario,Reseña
)

# ------------------------
# Usuario (Registro Cliente)
# ------------------------
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'nombre', 'direccion', 'telefono', 'es_dueño', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        usuario = Usuario.objects.create(**validated_data)
        send_mail(
            'Confirmación de Registro',
            'Gracias por registrarte en nuestro sistema.',
            'Gimnasio Web',
            [usuario.email],
            fail_silently=False,
        )
        return usuario

# ------------------------
# Gimnasio
# ------------------------
class GimnasioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gimnasio
        fields = '__all__'


# ------------------------
# Favorito
# ------------------------
class FavoritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorito
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorito.objects.all(),
                fields=['usuario', 'gimnasio'],
                message="Ya está marcado como favorito."
            )
        ]


# ------------------------
# Rutinas
# ------------------------
class RutinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rutina
        fields = '__all__'


# ------------------------
# Inventario
# ------------------------
class InventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventario
        fields = '__all__'


# ------------------------
# Maquinas
# ------------------------
class MaquinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maquina
        fields = '__all__'

# ------------------------
# Maquinas
# ------------------------

class ReseñaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reseña
        fields = '__all__'
        read_only_fields = ['usuario']  # <- esto es lo importante

    def validate(self, data):
        # Verificar que no exista ya una reseña del mismo usuario para el mismo gimnasio
        usuario = self.context['request'].user
        gimnasio = data.get('gimnasio')
        
        # Si es una actualización, excluir la reseña actual
        if self.instance:
            existing_resena = Reseña.objects.filter(
                usuario=usuario, 
                gimnasio=gimnasio
            ).exclude(pk=self.instance.pk).first()
        else:
            existing_resena = Reseña.objects.filter(
                usuario=usuario, 
                gimnasio=gimnasio
            ).first()
        
        if existing_resena:
            raise serializers.ValidationError(
                "Ya has dejado una reseña para este gimnasio. Solo puedes dejar una reseña por gimnasio."
            )
        
        return data

    def validate_estrellas(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La calificación debe estar entre 1 y 5 estrellas.")
        return value

    def validate_texto(self, value):
        if value and len(value) > 500:
            raise serializers.ValidationError("El comentario no puede exceder los 500 caracteres.")
        return value