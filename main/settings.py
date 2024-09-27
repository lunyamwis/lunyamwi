import os
from pathlib import Path
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-jcfkm1q@7_i1)eq@2&emyb)ixr2do3ozt^ab!o^w-dbgq)ognj'

# SECURITY WARNING: don't run with debug turned on in production!
CSRF_COOKIE_SECURE = False  # Set to True if using HTTPS
CSRF_COOKIE_HTTPONLY = True


DEBUG = True
ALLOWED_HOSTS = [
    f"{os.environ.get('DOMAIN1', '')}.boostedchat.com",
    f"{os.environ.get('DOMAIN2', '')}.boostedchat.com",
    # "*",
    "34.138.81.48",
    "34.74.147.25",
    "api.boostedchat.com",
    "elth.uk.boostedchat.com",
    "127.0.0.1",
    "localhost",
    "api.booksy.us.boostedchat.com",
    "booksy.us.boostedchat.com",
    "promptemplate.boostedchat.com",
    "promptemplate.booksy.boostedchat.com",
    "ce2d-105-161-11-162.ngrok-free.app",
    "ed48-196-105-37-1.ngrok-free.app",
    "6c71-35-195-79-196.ngrok-free.app",
    "prompt",
    "8000-lunyamwidev-promptempla-4xgxd6dimeq.ws-eu111.gitpod.io",
    "8000-lunyamwidev-promptempla-4xgxd6dimeq.ws-eu114.gitpod.io",
    "e098-34-78-218-130.ngrok-free.app",
    "739f-89-117-48-189.ngrok-free.app",
    "e39e-104-155-20-129.ngrok-free.app",
    "0610-34-38-36-1.ngrok-free.app",
    "77a3-34-38-36-1.ngrok-free.app",
    "c15f-34-38-194-170.ngrok-free.app",
    "2f6d-35-195-206-126.ngrok-free.app",
    "6f38-35-187-11-61.ngrok-free.app",
    "a306-34-79-189-161.ngrok-free.app",
    "e210-34-38-191-203.ngrok-free.app",
    "5249-34-38-191-203.ngrok-free.app",
    "7779-34-140-43-49.ngrok-free.app",
    "d7c9-34-79-50-211.ngrok-free.app",
    "42b8-104-199-87-142.ngrok-free.app",
    "62cf-2c0f-2a80-10e1-4210-ef30-78b8-6588-64e2.ngrok-free.app",
    "1624-195-26-252-153.ngrok-free.app",
    "f929-195-26-252-153.ngrok-free.app",
    "0060-195-26-252-153.ngrok-free.app",
    "f604-195-26-252-153.ngrok-free.app",
    "89b9-195-26-252-153.ngrok-free.app"
]

CSRF_TRUSTED_ORIGINS = [
    f"https://api.{os.environ.get('DOMAIN1', '')}.boostedchat.com",
    f"https://promptemplate.{os.environ.get('DOMAIN1', '')}.boostedchat.com",
    f"https://api.{os.environ.get('DOMAIN2', '')}.boostedchat.com",
    f"https://promptemplate.{os.environ.get('DOMAIN2', '')}.boostedchat.com",
    "https://api.boostedchat.com",
    "http://prompt",
    "https://api.booksy.us.boostedchat.com",
    "http://promptemplate.boostedchat.com",
    "http://promptemplate.booksy.boostedchat.com",
    "https://promptemplate.booksy.boostedchat.com",
    "https://8000-lunyamwidev-promptempla-4xgxd6dimeq.ws-eu111.gitpod.io/",
    "https://8000-lunyamwidev-promptempla-4xgxd6dimeq.ws-eu114.gitpod.io",
    "https://6c71-35-195-79-196.ngrok-free.app/",
    "https://e098-34-78-218-130.ngrok-free.app",
    "https://e39e-104-155-20-129.ngrok-free.app",
    "https://0610-34-38-36-1.ngrok-free.app",
    "https://77a3-34-38-36-1.ngrok-free.app",
    "https://c15f-34-38-194-170.ngrok-free.app",
    "https://2f6d-35-195-206-126.ngrok-free.app",
    "https://6f38-35-187-11-61.ngrok-free.app",
    "https://a306-34-79-189-161.ngrok-free.app",
    "https://a306-34-79-189-161.ngrok-free.app",
    "https://e210-34-38-191-203.ngrok-free.app",
    "https://5249-34-38-191-203.ngrok-free.app",
    "https://7779-34-140-43-49.ngrok-free.app",
    "https://d7c9-34-79-50-211.ngrok-free.app",
    "https://42b8-104-199-87-142.ngrok-free.app",
    "https://739f-89-117-48-189.ngrok-free.app",
    "https://62cf-2c0f-2a80-10e1-4210-ef30-78b8-6588-64e2.ngrok-free.app",
    "https://1624-195-26-252-153.ngrok-free.app",
    "https://f929-195-26-252-153.ngrok-free.app",
    "https://0060-195-26-252-153.ngrok-free.app",
    "https://f604-195-26-252-153.ngrok-free.app",
    "https://89b9-195-26-252-153.ngrok-free.app"
]

CORS_ALLOWED_ORIGINS = [
    f"https://api.{os.environ.get('DOMAIN1', '')}.boostedchat.com",
    f"https://promptemplate.{os.environ.get('DOMAIN1', '')}.boostedchat.com",
    f"https://api.{os.environ.get('DOMAIN2', '')}.boostedchat.com",
    f"https://promptemplate.{os.environ.get('DOMAIN2', '')}.boostedchat.com",
    f"https://{os.environ.get('DOMAIN2', '')}.boostedchat.com",
    "http://localhost:5173",
    "http://34.121.32.131",
    "https://34.121.32.131",
    "http://104.197.153.127",
    "https://104.197.153.127",
    "http://app.boostedchat.com",
    "http://promptemplate.booksy.boostedchat.com",
    "https://promptemplate.booksy.boostedchat.com",
]

CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)


CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "corsheaders",
    'rest_framework',
    'softdelete',
    'product',
    'prompt',
    'helpers'
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

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

WSGI_APPLICATION = 'main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_PROMPTFACTORY_DBNAME").strip(),
        "USER": os.getenv("POSTGRES_PROMPTFACTORY_USERNAME").strip(),
        "PASSWORD": os.getenv("POSTGRES_PROMPTFACTORY_PASSWORD").strip(),
        "HOST": os.getenv("POSTGRES_PROMPTFACTORY_HOST").strip(),
        "PORT": os.getenv("POSTGRES_PROMPTFACTORY_PORT").strip(),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = '/usr/src/app/static'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


USE_TZ = True
TIME_ZONE = 'UTC'  # Set to your desired time zone, e.g., 'America/New_York'
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER").strip()
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD").strip()
EMAIL_PORT = 587
EMAIL_USE_TLS = True
