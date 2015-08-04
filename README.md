django-oneskyapp
================

Django management command for maintaining OneSky localization in your django app.

>The idea is to have simple django management command which will pull, make messages, push, compile messages in that order into OneSky project. You only have to maintain your translation in OneSky. Run this command when new string will arise in your app or when you translate some strings in OneSky.

Instalation
---
```sh
$ python setup.py install
```
or 

```sh
$ pip install django-oneskyapp
```
Note to myself: "pip install --upgrade --no-deps django-oneskyapp" will upgrade without dependencies :)

Configuration
---

Add to your settings.py

```sh
INSTALLED_APPS = (
    ...
    'django_oneskyapp'
)

USE_I18N = True
USE_L10N = True

_ = lambda s: s
LANGUAGE_CODE = 'en'
LANGUAGES = (
	('en', _('English')),
	('sk', _('Slovak')),
	('de-AT', _('German (Austria)')),
	('pt-BR', _('Portuguese (Brazilian)')),
)

ONESKY_API_KEY = "my_public_key"
ONESKY_API_SECRET = "its_secret"
ONESKY_PROJECTS = [project_id] # Included in url as slug when translating or in projects list

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'testapp/locale'),
)

```


Usage
---
Don't forget to backup your locales if already translated, then run "oneskyapp" command
```sh
$ cd /your/django/app 
$ python manage.py oneskyapp
```

Known issues
---
- This workflow somehow does not work with django.po files manualy created in OneSky. OneSky API will respond with 400 error "This file is not downloadable through API". When creating OneSky project, always upload empty django.po file, do not create it by adding translation strings "manualy" in OneSky. 

- makemessages exception "CommandError: This script should be run from the Django Git tree or your project or app tree. If you did indeed run it from the Git checkout or your project or application..." Solution: makemessages does not like being run from project root, rather from app root. Change directory to your django app ```cd /your/django/project/app``` then call manage.py with proper path ```python /your/django/project/manage.py oneskyapp;``` If location of your templates is outside app directory, create symlink to your app so makemessages can scan templates through symlink. Same exception issue appers when running makemessages manualy, so again cd to your app dir then call ```manage.py makemessages -a -s``` with proper path and use -s switch to follow symlinks.

New to OneSky?
---
OneSky is awesome free localization management tool. It also offers profesional translation services. Create your free account at http://www.oneskyapp.com

How to OneSky?
---
- Create project
- Choose website/webapp, private/public
- Choose default language (professional translation service only works with english as default)
- Upload empty django.po file, or also upload all your translated django.po files and select proper language for them.
- Choose language pairs (according to uploaded translations and your django app settings)
- Translate or order translation using OneSky
- Mark translations as "ready to publish"

---

- Configure your django app for django-oneskyapp tool
- Use manage.py oneskyapp management command to pull, make, push, compile translations
- Restart your django app

---

- Add new strings to your django app
- Use manage.py oneskyapp
- Translate using OneSky
- Use manage.py oneskyapp
- Restart your django app

---

Have fun. 
Feel free to fork on GitHub or send an e-mail to stefan@backor.sk


