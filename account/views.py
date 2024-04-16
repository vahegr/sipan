from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.viewsets import ModelViewSet
from rest_framework import fields, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from subscription.serializer import SectionSerializer
from .serializers import UserSerializer
from .models import User
from subscription.models import Subscription


class ValidateQueryParams(serializers.Serializer):
    search = fields.RegexField(
        "^[0-9]{3,30}$",
        required=False
    )


class UsersViewSet(ModelViewSet):
    # queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        # query_params = ValidateQueryParams(data=self.request.query_params)
        # query_params.is_valid(raise_exception=True)
        query_dict = {k: v for k, v in self.request.query_params.items() if v}

        queryset = User.objects.filter(Q(is_superuser=False) | Q(is_staff=False))

        search_val = query_dict.get('search')
        if search_val:
            queryset = User.objects.filter(Q(national_code__icontains=search_val) | Q(first_name__icontains=search_val) | Q(last_name__icontains=search_val))
        return queryset

    @action(detail=True, methods=['get'])
    def subscriptions(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user_sections = Subscription.objects.filter(user=user).values_list("year__year", "year__section__name")
        user_section_subs = [f"{u[1]} {u[0]}" for u in user_sections]
        return Response(user_section_subs)
    
