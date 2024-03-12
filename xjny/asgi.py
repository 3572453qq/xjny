"""
ASGI config for xjny project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xjny.settings')
# django.setup()
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import lims.routing


print('*'*50,'in asgi.py')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xjny.settings')

application = ProtocolTypeRouter({
    "http":get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            lims.routing.websocket_urlpatterns
        )
    ),
})
