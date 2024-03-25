from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, serializers

from account.models import User
from sipan.settings import REST_FRAMEWORK

from .serializer import SectionSubscriptionSerializer, SubscriptionSerializer, SectionSerializer
from .models import Subscription, Section

from datetime import datetime

class UserSubsViewSet(ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def retrieve(self, request, pk=None):
        data = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True) 
        if self.queryset.filter(user=request.data['national_code'], section=request.data['section'], year=request.data['year']):
            return Response({"year": ["subscription the same year and section already exists."]}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubWithNationalCode(ViewSet):
    class SectionSubscriptionSerializer(serializers.Serializer):
        # todo validators
        year = serializers.IntegerField()
        national_code = serializers.CharField()
        section = serializers.IntegerField()

        def create(self, validated_data):
            user_obj = get_object_or_404(User.objects.all(), national_code=validated_data['national_code'])
            section_obj = get_object_or_404(Section.objects.all(), pk=validated_data['section'])
            return Subscription.objects.create(user=user_obj, section=section_obj, year=validated_data['year'])

        def save(self):
            self.create(self.validated_data).save()
            
    serializer_class = SectionSubscriptionSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        print(serializer)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class AvailableYears(ViewSet): 
    def list(self, request):
        year_backlim_diff = 2
        year_diff = 3
        current_year = datetime.now().year
        years = [current_year - year_backlim_diff + i for i in range(year_backlim_diff)] + [current_year + i for i in range(year_diff+1)]
        return Response(years)

class SectionViewSet(ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    pagination_class = PageNumberPagination

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        section = self.get_object()
        subscriptions = Subscription.objects.filter(section=section.pk).order_by('-year').all()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(subscriptions, request)
        subscriptions_serializer = SectionSubscriptionSerializer(page, many=True)
        data = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(data)
        return Response({
            **serializer.data,
            "count": len(subscriptions),
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": subscriptions_serializer.data
        })
