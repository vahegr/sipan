from rest_framework.routers import DefaultRouter
from .views import UserSubsViewSet, SectionViewSet

app_name = 'subscription'

router = DefaultRouter()

urlpatterns = [
    # path('api/register', views.Register.as_view(), name='account_register'),
] + router.urls