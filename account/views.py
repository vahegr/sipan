from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from .permissions import OwnerOrRead
from .serializers import UserSerializer
from .models import User


class UsersViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ('update', 'create', 'destroy', 'partial_update'):
            self.permission_classes = [IsAdminUser, ]
        return super(UsersViewSet, self).get_permissions()


# class Register(GenericAPIView):
#     serializer_class = RegisterSerializer
#
#     def post(self, request, *args,  **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         return Response({
#             "user": UserSerializer(user, context=self.get_serializer_context()).data,
#             "message": "User Created Successfully.  Now perform Login to get your token",
#         })
