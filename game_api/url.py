from django.urls import path, include
from rest_framework import routers
from .views.__init__ import *


router = routers.DefaultRouter()
router.register(r'videogames', VideoGameViewSet, 'videogames')

urlpatterns = [
    path('api/', include(router.urls))
]