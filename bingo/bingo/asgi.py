"""
ASGI config for bingo project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import bingoAPI.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo.settings')

# Ensure Django apps are initialized
django.setup()

# Define the ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(
            bingoAPI.routing.websocket_urlpatterns  # WebSocket routes
        )
    ),
})
