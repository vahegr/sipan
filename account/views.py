from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework import fields, serializers


from .serializers import UserSerializer
from .models import User


class ValidateQueryParams(serializers.Serializer):
    search = fields.RegexField(
        "^[0-9]{3,30}$",
        required=False
    )

class UsersViewSet(ModelViewSet):
    # queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        """
        Searches the database in relation to the query sent by the user.
        :return: Django queryset object containing search results.
        """
        query_params = ValidateQueryParams(data=self.request.query_params)
        query_params.is_valid(raise_exception=True)
        query_dict = {k: v for k, v in self.request.query_params.items() if v}
        filter_keyword_arguments_dict = {}
        for key, value in query_dict.items():
            if key == "search":
                filter_keyword_arguments_dict["national_code__icontains"] = value
        queryset = User.objects.filter(**filter_keyword_arguments_dict)
        return queryset
