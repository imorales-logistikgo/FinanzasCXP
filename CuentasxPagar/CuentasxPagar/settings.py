"""
Django settings for CuentasxPagar project.

Generated by 'django-admin startproject' using Django 2.1.13.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '72%&=!1sfmlmq22xb=^=ucc5t32fbh1p=o2h26wj3y(u4g0%1z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'debug_toolbar',
    'corsheaders',
    'PendientesEnviar',
    'Dashboard',
    'EstadosCuenta',
    'ReporteFacturas',
    'ReportePagos',
    'ReporteCanceladas',
    'ReportePagosCancelados',
    'users',
    'usersadmon',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

ROOT_URLCONF = 'CuentasxPagar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'CuentasxPagar.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'PruebaDjango',
        'HOST': '104.210.157.194',
        'PORT': '1433',
        'USER': 'sa',
        'PASSWORD': 'iLs8iC9S69',

        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        }
    },
    'users': {
        'ENGINE': "sql_server.pyodbc",
        'NAME': "LogistikGo_Admon",
        'HOST': "104.210.157.194",
        'USER': "sa",
        'PASSWORD': "iLs8iC9S69",
        'PORT': "1433",
        'OPTIONS': {
            'driver': "ODBC Driver 17 for SQL Server",
        },
    }
}

DATABASE_ROUTERS = ['users.router.AuthRouter',]

AUTHENTICATION_BACKENDS = (
    'users.backends.EmailBackend',
    )


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

INTERNAL_IPS= ['127.0.0.1',]
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = "/StaticFinal/"

AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = '/PendientesEnviar/'
SESSION_COOKIE_AGE = 21600