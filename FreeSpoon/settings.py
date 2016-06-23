"""
Django settings for FreeSpoon project.

Generated by 'django-admin startproject' using Django 1.9.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xp2b_@+6nn&w0l)r)sk$h3n59%)esdv8b+*$g0wbewli^i1dr#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.messages',
    'django.contrib.staticfiles',
    'authentication',

    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',

    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.weixin',

    'basic',
    'api',
    'business',
]

SITE_ID = 1

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    #'django.contrib.sessions.middleware.SessionMiddleware',
    'FreeSpoon.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'FreeSpoon.middleware.AuthenticationMiddleware',
    #'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'FreeSpoon.urls'

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

WSGI_APPLICATION = 'FreeSpoon.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'FreeSpoon',
	'USER': 'root',
	'PASSWORD': os.getenv('DBPASSWD'),
	'HOST': os.getenv('DBHOST'),
	'PORT': '3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'zh-CN'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = False

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
	'file': {
	    'level': 'DEBUG',
	    'class': 'logging.FileHandler',
	    'filename': '/var/log/django.log',
	},
    },
    'loggers': {
	'django': {
	    'handlers': ['file'],
	    'level': 'DEBUG',
	    'propagate': True,
	},
    },
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'authentication.authentication.SmsBackend',
)

REST_USE_JWT = True

REST_AUTH_SERIALIZERS = {
    'JWT_SERIALIZER': 'authentication.serializers.JWTSerializer',
    'USER_DETAILS_SERIALIZER': 'authentication.serializers.MobUserSerializer',
    'LOGIN_SERIALIZER': 'authentication.serializers.LoginSerializer',
}

REST_SESSION_LOGIN = False

SOCIALACCOUNT_PROVIDERS = {
    'weixin': {
        'AUTHORIZE_URL': 'https://open.weixin.qq.com/connect/oauth2/authorize', # Not Used
        'SCOPE': ('snsapi_userinfo',),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
}

JWT_AUTH = {
    'JWT_PAYLOAD_GET_USERNAME_HANDLER':
    'authentication.utils.jwt_get_username_from_payload_handler',
    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'business.serializers.jwt_response_payload_handler',

    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=30),
    #'JWT_EXPIRATION_DELTA': datetime.timedelta(minutes=2),
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=999),
}

AUTH_USER_MODEL = 'authentication.MobUser'

ACCOUNT_USER_MODEL_USERNAME_FIELD = 'mob'
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_ADAPTER = 'authentication.adapter.DefaultAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'authentication.adapter.DefaultSocialAccountAdapter'

