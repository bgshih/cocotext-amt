"""
Django settings for server project.

Generated by 'django-admin startproject' using Django 1.11.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=1k1i!1z9z9dih@e!+fhc(yez4!vxwun6r&q7a^5$ek%j+oyxs'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Use MTurk development sandbox
MTURK_SANDBOX = False

# Use a separate database in development
DATABASE_NAME = 'cocotext_v2'

ALLOWED_HOSTS = [
    # 'amt-api.bgshi.me'
    '*' # TODO: change in production
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'common.apps.CommonConfig',
    'polyverif.apps.PolyverifConfig',
    'polyannot.apps.PolyannotConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'server.urls'

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

WSGI_APPLICATION = 'server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DATABASE_NAME,
        'USER': 'cocotext',
        'PASSWORD': 'w2PtkwRhThtyA',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATIC_URL = '/static/'


# MTurk settings
MTURK_ENDPOINT_URL = \
    'https://mturk-requester-sandbox.us-east-1.amazonaws.com' if MTURK_SANDBOX else \
    'https://mturk-requester.us-east-1.amazonaws.com'

# ratio of crop margin to the squared root of bounding box area
TEXT_INSTANCE_CROP_MARGIN_RATIO = 1.0

# Directory of the MSCOCO images
LOCAL_COCO_IMAGE_DIR = '/home/ubuntu/data/coco-images/train2014'

# Polygon verification
POLYVERIF_NUM_CONTENT_PER_TASK = 9
POLYVERIF_SENTINEL_PORTION = 0.05
POLYVERIF_MIN_CONSENSUS_COUNT = 3

# Polygon annotation
COCOTEXT_IMAGE_URL_TEMPLATE = 'https://s3.amazonaws.com/cocotext-images/train2014/COCO_train2014_{:0>12}.jpg'
