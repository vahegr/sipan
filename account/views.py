from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import login


from .serializers import UserSerializer
from .models import User

class UsersViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ('update', 'create', 'destroy', 'partial_update'):
            self.permission_classes = [IsAdminUser, ]
        return super(UsersViewSet, self).get_permissions()

