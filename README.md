# DermaChat

**DermaChat** es una plataforma web desarrollada en **Django** que ofrece un análisis preliminar del acné mediante **inteligencia artificial**, permitiendo a los usuarios resolver sus dudas sobre el estado de su piel de forma rápida y accesible.

El sistema está diseñado bajo una **arquitectura cliente-servidor**, donde el cliente (interfaz web) interactúa con un servidor Django que gestiona los usuarios, el envío de mensajes y el análisis automatizado.

---

## Tabla de Contenidos

- [Descripción del Proyecto](#-descripción-del-proyecto)
- [Características Principales](#-características-principales)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Requisitos Previos](#-requisitos-previos)
- [Configuración del Entorno](#-configuración-del-entorno)
- [Instalación y Ejecución](#-instalación-y-ejecución)
- [Configuración de Variables de Entorno](#-configuración-de-variables-de-entorno)
- [API Endpoints](#-api-endpoints)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Autores](#-autores)
- [Consideraciones Importantes](#-consideraciones-importantes)

---

## Descripción del Proyecto

DermaChat permite a los usuarios:

- Crear una cuenta y acceder a su perfil personalizado
- Enviar mensajes y dudas sobre su piel mediante un chat interactivo
- Subir imágenes que son analizadas por un modelo de **IA dermatológica**
- Recibir sugerencias personalizadas y recomendaciones informativas basadas en el análisis
- Consultar información médica verificada de fuentes reconocidas
- Gestionar múltiples conversaciones con historial completo
- Acceder a planes premium con funcionalidades adicionales
- Recuperar contraseña mediante verificación por email
- Verificar cuenta mediante enlace de confirmación

El objetivo principal es **brindar orientación previa** a la consulta con un dermatólogo, ayudando a identificar posibles tipos de acné o afecciones comunes, **sin reemplazar la opinión profesional**.

---

## Características Principales

### Autenticación y Seguridad
- Sistema de autenticación personalizado con modelo de usuario extendido
- Verificación de email obligatoria para activar cuenta
- Recuperación de contraseña mediante tokens seguros
- Protección CSRF en todas las peticiones
- Sesiones seguras con Django

### Chat con IA
- Integración con `VoiceFlow` para conversaciones inteligentes
- Análisis de imágenes en tiempo real con `RoboFlow`
- Historial completo de conversaciones
- Interfaz de chat moderna y responsiva
- Soporte para envío de imágenes y texto

### Análisis de Imágenes
- Detección automática de severidad del acné (leve, moderado, severo)
- Identificación de características específicas en las lesiones
- Integración con modelo de IA especializado en dermatología
- Procesamiento de imágenes con OpenCV y PIL

### Sistema de Pagos
- Integración con **Mercado Pago** para planes premium
- Integracion con **PayPal** a través de la API de pagos
- Gestión de pagos
- Páginas de confirmación de pago (éxito, fallo, pendiente)

### Notificaciones por Email
- Envío de emails de verificación de cuenta
- Recuperación de contraseña por email
- Configuración SMTP con Gmail

---

## Estructura del Proyecto

```
DermaChat/
│
├── backend/                    # Configuración principal de Django
│   ├── __init__.py
│   ├── settings.py            # Configuración del proyecto
│   ├── urls.py                # URLs principales
│   ├── wsgi.py                # WSGI para producción
│   └── asgi.py                # ASGI para producción
│
├── core/                       # Aplicación principal
│   ├── migrations/            # Migraciones de base de datos
│   ├── static/core/           # Archivos estáticos
│   │   ├── css/              # Estilos CSS
│   │   ├── js/               # JavaScript
│   │   └── img/              # Imágenes estáticas
│   ├── templates/core/       # Plantillas HTML
│   ├── management/commands/  # Comandos personalizados
│   ├── models.py             # Modelos de datos (Usuario, Conversacion, Mensaje)
│   ├── views.py              # Vistas y lógica de negocio
│   ├── urls.py               # URLs de la aplicación
│   ├── serializers.py        # Serializadores para API REST
│   └── forms.py              # Formularios Django
│
├── ChatBot-IA/                # Módulo de procesamiento de IA
│   ├── Acne-BD/              # Base de datos de imágenes de entrenamiento
│   ├── PDFS/                 # Documentación médica en PDF
│   ├── image_processor.py    # Procesamiento de imágenes
│   ├── pdf_reader.py         # Lector de PDFs
│   └── config.py             # Configuración del módulo IA
│
├── media/                     # Archivos subidos por usuarios
│   └── perfiles/             # Fotos de perfil
│
├── manage.py                  # Script de administración de Django
├── requirements.txt           # Dependencias del proyecto
├── db.sqlite3                 # Base de datos SQLite (desarrollo)
├── .env                       # Variables de entorno (crear manualmente)
└── README.md                  # Este archivo
```

---

## Requisitos Previos

### Como usuario
No necesitas tener nada instalado, solo acceder a través del navegador web a DermaChat.

### Como developer
Se debe de tener instalado:

- **Python 3.11 o superior**
- **pip** (gestor de paquetes de Python)
- **Git** (para clonar el repositorio)
- `.env` con las llaves secretas (API) de:
  - gmail
  - mercadopago
  - RoboFlow
  - VoiceFlow
---

## Configuración del Entorno

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd DermaChat
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

---

## Instalación y Ejecución

### Pasos para ejecutar el proyecto localmente:

```bash
# 1. Activar el entorno virtual (si no está activado)
venv\Scripts\activate  # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear archivo .env (ver sección siguiente)
# Copia el ejemplo y completa con tus credenciales

# 4. Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# 6. Ejecutar servidor de desarrollo
python manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000/`

---

## Configuración de Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# VoiceFlow API - Para el chat con IA
VOICEFLOW_API_KEY=tu_api_key_de_voiceflow

# Roboflow API - Para análisis de imágenes
ROBOFLOW_API_KEY=tu_api_key_de_roboflow
ROBOFLOW_MODEL_ID=tu_model_id
ROBOFLOW_VERSION=1

# Email Configuration - Para envío de emails
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion

# Mercado Pago - Para pagos (opcional)
MERCADOPAGO_ACCESS_TOKEN=tu_access_token_de_mercadopago

# Django Secret Key (opcional, ya hay una por defecto para desarrollo)
SECRET_KEY=tu_secret_key_segura
```

### Notas sobre las Variables de Entorno:

- **VOICEFLOW_API_KEY**: Obtén tu API key desde el dashboard de VoiceFlow
- **ROBOFLOW_API_KEY**: Disponible en tu cuenta de Roboflow
- **EMAIL_HOST_PASSWORD**: Usa una **contraseña de aplicación** de Gmail, no tu contraseña normal
  - Cómo obtenerla: [Configurar contraseña de aplicación Gmail](https://support.google.com/accounts/answer/185833)
- **MERCADOPAGO_ACCESS_TOKEN**: Obtén tu token desde el panel de Mercado Pago

---

## API Endpoints

### Endpoints de Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/registro/` | Registrar nuevo usuario |
| `POST` | `/api/login/` | Iniciar sesión (retorna token) |
| `GET` | `/login-page/` | Página HTML de login |
| `GET` | `/register-page/` | Página HTML de registro |
| `POST` | `/login-usuario/` | Login desde formulario HTML |
| `GET` | `/logout/` | Cerrar sesión |

### Endpoints de Usuario

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/profile` | Ver perfil del usuario |
| `GET` | `/edit-profile/` | Editar perfil |
| `POST` | `/eliminar-cuenta-usuario/` | Eliminar cuenta |

### Endpoints de Chat

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/chat/` | Página del chat |
| `GET` | `/api/conversaciones/` | Listar conversaciones del usuario |
| `POST` | `/api/conversaciones/` | Crear nueva conversación |
| `GET` | `/api/mensajes/` | Listar mensajes (filtrado por conversación) |
| `POST` | `/api/mensajes/` | Crear nuevo mensaje |
| `POST` | `/api/analyze_image/` | Analizar imagen de acné |

### Endpoints de Recuperación de Contraseña

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/recuperar/` | Página de recuperación |
| `GET` | `/reestablecer/<token>/` | Restablecer contraseña con token |

### Endpoints de Verificación de Email

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/verificar-email/<token>/` | Verificar email con token |
| `POST` | `/reenviar-verificacion/` | Reenviar email de verificación |

### Endpoints de Pagos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/select-plan/` | Seleccionar plan premium |
| `GET` | `/payment-options/` | Opciones de pago |
| `GET` | `/payment/success/` | Pago exitoso |
| `GET` | `/payment/failure/` | Pago fallido |
| `GET` | `/payment/pending/` | Pago pendiente |

### Endpoints de Contacto

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/Contacto/` | Página de contacto |
| `GET` | `/contacto/enviado/` | Confirmación de contacto enviado |

---

## Tecnologías Utilizadas

### Backend
- **Python 3.11+** - Lenguaje de programación
- **Django 5.2.1** - Framework web
- **Django REST Framework 3.15.2** - API REST
- **django-cors-headers 4.3.1** - Manejo de CORS
- **python-decouple 3.8** - Gestión de variables de entorno
- **Pillow 10.2.0** - Procesamiento de imágenes
- **django-filter 23.5** - Filtrado de datos
- **requests 2.31.0** - Peticiones HTTP

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos
- **JavaScript (ES6+)** - Interactividad
- **Materialize CSS** - Framework CSS

### Base de Datos
- **SQLite3** - Base de datos (desarrollo)

### Servicios Externos
- **VoiceFlow API** - Chat con inteligencia artificial
- **Roboflow API** - Análisis de imágenes con IA
- **Mercado Pago API** - Procesamiento de pagos
- **Gmail SMTP** - Envío de emails

### Procesamiento de Imágenes
- **OpenCV (cv2)** - Procesamiento de imágenes
- **NumPy** - Operaciones numéricas
- **PIL/Pillow** - Manipulación de imágenes

---

## Modelos de Datos

#### Usuario
- Email (único)
- Nombre
- Edad (opcional)
- Foto de perfil
- Email verificado (boolean)
- Es premium (boolean)
- Tokens de recuperación y verificación

#### Conversacion
- Usuario (ForeignKey)
- Título
- Fecha de creación

#### Mensaje
- Conversación (ForeignKey)
- Remitente (usuario/IA)
- Contenido
- Fecha de creación

### Flujo de Análisis de Imágenes

1. Usuario sube imagen en el chat
2. Imagen se envía a `/api/analyze_image/`
3. Backend procesa imagen con Roboflow API
4. Se detecta severidad y características del acné
5. Resultado se envía a VoiceFlow para generar recomendaciones
6. Respuesta se muestra al usuario en el chat

### Flujo de Chat con IA

1. Usuario envía mensaje o imagen
2. Si es imagen, se analiza primero con Roboflow
3. Mensaje (o resultado del análisis) se envía a VoiceFlow
4. VoiceFlow genera respuesta contextual
5. Respuesta se guarda en base de datos
6. Mensaje se muestra en la interfaz

---

## Autores

- **Alejandro Garzón**
- **Santiago Useche**
- **Miguel Arboleda**

---

## ⚠️ Consideraciones Importantes

### Uso Médico
- **DermaChat NO reemplaza la consulta médica profesional**
- Los análisis y recomendaciones ofrecidos son **orientativos** y tienen **fines educativos**
- Siempre consulta con un dermatólogo certificado para diagnósticos y tratamientos, de igual forma, DermaChat nuncá te dara diagnosticos definitivos y siempre recomendara consulta profesional.

### Límites de API
- VoiceFlow tiene límites de uso
- Roboflow tiene límites de inferencias
- Mercado Pago tiene límites

---

**Última actualización**: 12/2025
