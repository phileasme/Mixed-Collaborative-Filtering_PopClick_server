"""
WSGI config for mainsite project.

It exposes the WSGI callable as a module-level variable named ``application``.

@provided by default
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mainsite.settings")

application = get_wsgi_application()
