from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import UsersViewSet

app_name = 'account'


router = DefaultRouter()


urlpatterns = [

] + router.urls
