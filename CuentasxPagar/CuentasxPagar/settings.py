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

CORS_ORIGIN_ALLOW_ALL = True

# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'debug_toolbar',
    'PendientesEnviar',
    'Dashboard',
    'EstadosCuenta',
    'ReporteFacturas',
    'ReportePagos',
    'ReporteCanceladas',
    'ReportePagosCancelados',
    'ReporteMaster',
    'EvidenciasProveedor',
    'users',
    'usersadmon',
    'bkg_viajes',
    'XD_Viajes'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
        'DIRS': [BASE_DIR + '/templates/'],
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
        'NAME': "LogistikGO_Admon_Django",
        'HOST': "logistikgo.database.windows.net",
        'USER': "QUR3n5qk4F33",
        'PASSWORD': "Hi0p68To45lzXp0klf",
        'PORT': "1433",
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        }
    },
    'users': {
        'ENGINE': "sql_server.pyodbc",
        'NAME': "LogistikGO_Admon_Copiar_01",
        'HOST': "logistikgo.database.windows.net",
        'USER': "QUR3n5qk4F33",
        'PASSWORD': "Hi0p68To45lzXp0klf",
        'PORT': "1433",
        'OPTIONS': {
            'driver': "ODBC Driver 17 for SQL Server",
        },
        #'ATOMIC_REQUESTS': True,
    },
    'bkg_viajesDB': {
         'ENGINE': "sql_server.pyodbc",
         'NAME': "LogistikGO_Brockeraje_Copiar_01",
         'HOST': "logistikgo.database.windows.net",
         'USER': "QUR3n5qk4F33",
         'PASSWORD': "Hi0p68To45lzXp0klf",
         'PORT': "1433",
         'OPTIONS': {
             'driver': "ODBC Driver 17 for SQL Server",
         },
     },
    'XD_ViajesDB': {
         'ENGINE': "sql_server.pyodbc",
         'NAME': "LogistikGO_LKMXD_Copiar_01",
         'HOST': "logistikgo.database.windows.net",
         'USER': "QUR3n5qk4F33",
         'PASSWORD': "Hi0p68To45lzXp0klf",
         'PORT': "1433",
         'OPTIONS': {
         'driver': "ODBC Driver 17 for SQL Server",
         },
      }
    # 'users': {
    #     'ENGINE': "sql_server.pyodbc",
    #     'NAME': "LogistikGO_Admon",
    #     'HOST': "logistikgo.database.windows.net",
    #     'USER': "QUR3n5qk4F33",
    #     'PASSWORD': "Kh216Dr97DPoZxxS57",
    #     'PORT': "1433",
    #     'OPTIONS': {
    #         'driver': "ODBC Driver 17 for SQL Server",
    #     },
    # }
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
LOGIN_URL = "/Usuario/Login/"
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = '/PendientesEnviar/'
SESSION_COOKIE_AGE = 21600
#SESSION_COOKIE_SECURE = True
#LOGOUT_REDIRECT_URL = "/Usuario/Login/"

#SECURE_SSL_REDIRECT = True
EMAIL_HOST = 'smtp.googlemail.com'
EMAIL_HOST_USER = 'pagos.proveedores@logistikgo.com'
EMAIL_HOST_PASSWORD = 'LogistiK20.1'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
