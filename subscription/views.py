from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from sipan.settings import REST_FRAMEWORK

from .serializer import SectionSubscriptionSerializer, SubscriptionSerializer, SectionSerializer
from .models import Subscription, Section


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

        if self.queryset.filter(user=request.data['user'], section=request.data['section'], year=request.data['year']):
            return Response({"year": ["subscription the same year and section already exists."]}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SectionViewSet(ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    pagination_class = PageNumberPagination

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        section = self.get_object()
        subscriptions = Subscription.objects.filter(section=section.pk).all()

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(subscriptions, request)
        print()

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

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
