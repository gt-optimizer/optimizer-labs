from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    'www.optimizer-labs.fr',
    'optimizer-labs.fr',
]

# Sécurité
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Fichiers statiques
STORAGES["staticfiles"]["BACKEND"] = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# Email pour les erreurs 500
ADMINS = [('Optimizer Labs', 'support@optimizer-labs.fr')]
SERVER_EMAIL = 'support@optimizer-labs.fr'

# Wagtail
WAGTAILADMIN_BASE_URL = 'https://www.optimizer-labs.fr'

# Logs — affiche les erreurs dans la console AlwaysData
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# Secrets dans local.py (jamais commité)
try:
    from .local import *
except ImportError:
    pass