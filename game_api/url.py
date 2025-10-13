from django.urls import path, include
from rest_framework import routers
from .views.__init__ import *


router = routers.DefaultRouter()
router.register(r'videogames', VideoGameViewSet, 'videogames')
router.register(r'users', UserViewSet, 'users')

urlpatterns = [
    path('api/', include(router.urls))
]