from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework import status

from .serializer import SubscriptionSerializer, SubSectionSerializer
from .models import Subscription, SubSection


class UserSubsViewSet(ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    # def list(self, request):
    #     queryset = Subscription.objects.all()
    #     serializer = SubscriptionSerializer(queryset, many=True)
    #     return Response(serializer.data)

    def retrieve(self, request, pk=None):
        print("HEre")
        data = get_object_or_404(Subscription, user=pk)
        serializer = SubscriptionSerializer(data)
        return Response(serializer.data)
    
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if self.queryset.filter(user=request.data['user'], sub=request.data['sub'], year=request.data['year']):
            return Response({"year": ["subscription section with this year already exists."]}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class SubSectionViewSet(ModelViewSet):
    queryset = SubSection.objects.all()
    serializer_class = SubSectionSerializer

    class Meta:
        fields = ('user', 'sub', 'year')

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        print("HEre")
        data = get_object_or_404(SubSection, user=pk)
        serializer = self.serializer_class(data)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

# class UserSubsViewSet(ModelViewSet):
#     queryset = Subscription.objects.all()
#     serializer_class = SubscriptionSerializer

#     def get_permissions(self):
#         if self.action in ('update', 'create', 'destroy', 'partial_update'):
#             self.permission_classes = [AllowAny, ]
#         return super(UserSubsViewSet, self).get_permissions()

# class SubSectionViewSet(ModelViewSet):
#     queryset = SubSection.objects.all()
#     serializer_class = SubSectionSerializer

#     def get_permissions(self):
#         if self.action in ('update', 'create', 'destroy', 'partial_update'):
#             self.permission_classes = [AllowAny, ]
#         return super(SubSectionViewSet, self).get_permissions()