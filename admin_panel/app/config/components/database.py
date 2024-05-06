import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('ADMIN_PANEL_POSTGRES_DB'),
        'USER': os.environ.get('ADMIN_PANEL_POSTGRES_USER'),
        'PASSWORD': os.environ.get('ADMIN_PANEL_POSTGRES_PASSWORD'),
        'HOST': os.environ.get('ADMIN_PANEL_POSTGRES_HOST', 'movies_db'),
        'PORT': os.environ.get('ADMIN_PANEL_POSTGRES_PORT', 5432),
        'OPTIONS': {
           'options': '-c search_path=public,content'
        }
    }
}