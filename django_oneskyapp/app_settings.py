from django.conf import settings


ONESKY_API_KEY = getattr(settings, 'ONESKY_API_KEY')
ONESKY_API_SECRET = getattr(settings, 'ONESKY_API_SECRET')
ONESKY_PROJECTS = getattr(settings, 'ONESKY_PROJECTS')
ONESKY_LOCALE_PATHS = getattr(
    settings, 'ONESKY_LOCALE_PATHS', settings.LOCALE_PATHS
)
ONESKY_LANGUAGES = getattr(settings, 'LANGUAGES', settings.LANGUAGES)
ONESKY_MAKEMESSAGES_COMMAND = getattr(
    settings, 'ONESKY_MAKEMESSAGES_COMMAND', 'makemessages'
)
ONESKY_COMPILEMESSAGES_COMMAND = getattr(
    settings, 'ONESKY_COMPILEMESSAGES_COMMAND', 'compilemessages'
)
