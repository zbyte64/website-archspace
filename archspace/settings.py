import os
PROJECT_NAME = "archspace"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = '%s/public/media/'%PROJECT_DIR
SECRET_KEY = 'ky6+w%yt-))m-auwl_)y2)rgn2xn57vewwixwa+u#ziy-6!h%z'

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'db.sqlite'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

ADMINS = (
    ('debug', 'debug@somewhere.net'),
)

# Setup Sites here
TIME_ZONE = 'US/Pacific'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1

# Setup locations here
DEBUG=True
MEDIA_ROOT = '%s/public/media/'%PROJECT_DIR
STATIC_ROOT = '%s/public/static/'%PROJECT_DIR
WEB_ROOT = '%s/public/static/' % PROJECT_DIR
TEMPLATE_DIRS = (
    '%s/templates'%PROJECT_DIR,
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.webdesign',
    'django.contrib.markup',
    'django.contrib.comments',
    'django.contrib.sitemaps',
    'django.contrib.admindocs',
    'archspace.controlmodel',
    'archspace.fleets',
    'archspace.game',
    'archspace.missions',
    'archspace.planets', 
    'archspace.players',
    'archspace.race',
    'archspace.rulebuilder',
    'archspace.technology',
)

ROOT_URLCONF="urls"

