"""
Django settings for core project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env Datei laden, damit wir SECRET_KEY etc. daraus lesen können
load_dotenv()

# Basis-Verzeichnis des Projekts (der Ordner in dem manage.py liegt)
BASE_DIR = Path(__file__).resolve().parent.parent

# Geheimer Schlüssel – wird aus .env geladen statt direkt im Code zu stehen
SECRET_KEY = os.getenv('SECRET_KEY')

# Debug-Modus – im Entwicklungsmodus True, in Produktion MUSS das False sein
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Welche Hosts dürfen auf das Backend zugreifen
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]

# Alle installierten Apps – Django-eigene + Drittanbieter + unsere eigenen
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Drittanbieter
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    # Eigene Apps
    'auth_app',
    'profiles_app',
    'offers_app',
    'orders_app',
    'reviews_app',
    'base_info_app',
]

# Middleware – Schichten die jede Anfrage durchläuft
# CORS Middleware MUSS ganz oben stehen!
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Datenbank – SQLite für Entwicklung
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Passwort-Validierung
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Sprache und Zeitzone
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Statische Dateien (CSS, JavaScript, Bilder)
STATIC_URL = 'static/'

# Medien-Dateien (z.B. hochgeladene Profilbilder)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Einstellungen
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

# CORS Einstellungen – Erlaubt dem Frontend mit dem Backend zu kommunizieren
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5500',
    'http://127.0.0.1:5500',
    'http://localhost:5501',
    'http://127.0.0.1:5501',
]