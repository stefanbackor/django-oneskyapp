"""
Django settings for testapp project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xk*l=1&^#3456ugf1-^z-#8qx@eq)zms&f-#ut78vm^60s_7^5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
	#'django.contrib.admin',
	#'django.contrib.auth',
	#'django.contrib.contenttypes',
	#'django.contrib.sessions',
	#'django.contrib.messages',
	#'django.contrib.staticfiles',
	'django_oneskyapp',
)

MIDDLEWARE_CLASSES = (
	#'django.contrib.sessions.middleware.SessionMiddleware',
	#'django.middleware.common.CommonMiddleware',
	#'django.middleware.csrf.CsrfViewMiddleware',
	#'django.contrib.auth.middleware.AuthenticationMiddleware',
	#'django.contrib.messages.middleware.MessageMiddleware',
	#'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'testapp.urls'

WSGI_APPLICATION = 'testapp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

_ = lambda s: s

LANGUAGE_CODE = 'en'
LANGUAGES = (
	('en', _('English')),
	('sk', _('Slovak')),
	('de-AT', _('German (Austria)')),
	('pt-BR', _('Portuguese (Brazilian)')),
)

ONESKY_API_KEY = ""
ONESKY_API_SECRET = ""
ONESKY_PROJECTS = [123]

LOCALE_PATHS = (os.path.join(BASE_DIR, 'testapp/locale'),)
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'testapp/templates')]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
