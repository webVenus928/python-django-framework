from .common import *


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'pynnydb.sqlite3'),
    }
}


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b&29+tkfw%m*=(%szs9=jld0_*rp&z)7f1y8l(idp%f0v+p_%$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
