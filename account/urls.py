from django.urls import path
from rest_framework.routers import DefaultRouter


from . import views

app_name = 'account'

router = DefaultRouter()
router.register(r'users', views.UsersViewSet, basename='users')

urlpatterns = [

    # path('api/register', views.Register.as_view(), name='account_register'),
]
urlpatterns += router.urls