# DermaChat

- **DermaChat** es una plataforma web desarrollada en **Django** que ofrece un análisis preliminar del acné mediante **inteligencia artificia**, permitiendo a los usuarios resolver sus dudas sobre el estado de su piel de forma rápida y accesible.

El sistema está diseñado bajo una **arquitectura cliente-servidor**, donde el cliente (interfaz web) interactúa con un servidor Django que gestiona los usuarios, el envío de mensajes y el análisis automatizado.

## **Descripción del Proyecto**

DermaChat permite a los usuarios:

- Crear una cuenta y acceder a su perfil.
- Enviar mensajes y dudas sobre su piel mediante un chat interactivo.
- Subir imágenes que son analizadas por un modelo de ***IA dermatológica****.
- Recibir sugerencias personalizadas y recomendaciones informativas.
- Consultar información médica verificada de fuentes reconocidas.

El objetivo principal es **brindar orientación previa** a la consulta con un dermatólogo, ayudando a identificar posibles tipos de acné o afecciones comunes, **sin reemplazar la opinión profesional**.

## **Estructura del Proyecto**

```python
DermaChat/

│

├── core/ 

│ ├── templates/core/ # Archivos HTML (frontend)

│ ├── static/core/ # Archivos estáticos (CSS, JS, imágenes)

│ ├── views.py

│ ├── models.py 

│ ├── forms.py 

│ └── urls.py 

│

├── backend/ 

│ ├── settings.py

│ ├── urls.py

│ └── wsgi.py

│

├── manage.py 

└── requirements.txt 
```

## **Ejecución**

Para ejecutar el proyecto localmente:

```python
python -m venv venv

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

python manage.py runserver
```

## **Tecnologías Utilizadas**

- `Python 3.11+`
- `Django 5.x`
- `HTML5, CSS, JavaScript`
- `Materialize CSS`
- `SQLite3`
- Inteligencia Artificial por la API de VoiceFlow

## **Autores**

- Alejandro Garzón
- Santiago Useche
- Miguel Arboleda

## **Consideraciones**

- DermaChat no reemplaza la consulta médica profesional.
- Los análisis y recomendaciones ofrecidos son orientativos y tienen fines educativos.