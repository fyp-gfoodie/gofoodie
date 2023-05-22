"""
ASGI config for final_fyp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from food.routing import websocket_urlpatterns
from channels.auth import AuthMiddleware, AuthMiddlewareStack
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'final_fyp.settings')

application = ProtocolTypeRouter({
    'https': get_asgi_application(),
    'websocket':AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})



