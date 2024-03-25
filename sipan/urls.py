from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from sipan.settings import BASE_DIR

from account.views import UsersViewSet
from subscription.views import UserSubsViewSet, SectionViewSet, AvailableYears, SubWithNationalCode

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register(r'users', UsersViewSet, basename='users')
router.register(r'subs', UserSubsViewSet, basename='subs')
router.register(r'sections/sub', SubWithNationalCode, basename='section reg')
router.register(r'sections', SectionViewSet, basename='sections')
router.register(r'years', AvailableYears, basename='years')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify')
] 

urlpatterns += static('users/images/', document_root=BASE_DIR / 'users' / 'images')
