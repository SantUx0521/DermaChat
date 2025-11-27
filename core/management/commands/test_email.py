from django.core.management.base import BaseCommand
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Prueba el envío de correos'

    def handle(self, *args, **options):
        try:
            send_mail(
                'Prueba de correo DermaChat',
                'Este es un correo de prueba para verificar la configuración de Gmail SMTP.',
                'noreply@gmail.com',
                ['dermachat@gmail.com'], 
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('Correo enviado exitosamente'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al enviar correo: {str(e)}')) 