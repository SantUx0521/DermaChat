from django.contrib import admin
from .models import Usuario, FichaBiometrica, Gimnasio, Inventario,ClienteGimnasio,Favorito,Rutina,Maquina

admin.site.register(Usuario)
admin.site.register(FichaBiometrica)
admin.site.register(Gimnasio)
admin.site.register(Inventario)
admin.site.register(ClienteGimnasio)
admin.site.register(Favorito)
admin.site.register(Rutina)
admin.site.register(Maquina)

class GimnasioAdmin(admin.ModelAdmin):
    list_display = ('nombre_gym', 'ubicacion', 'precio_inscripcion')
    fields = ('nombre_gym', 'ubicacion', 'precio_inscripcion', 'descripcion', 'vistas', 'dueño', 'imagen')