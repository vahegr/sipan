from datetime import datetime
from django.db.models import CharField, IntegerField
from django.shortcuts import get_object_or_404
from django.db.models import Q, F, OuterRef
from django.db.models.functions import Concat
from django.db.models import Value

from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework import fields, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from subscription.serializer import HistorySerializer, UserPaymentSerializer
from subscription.models import History, Subscription, SectionYear

from .serializers import ChangePasswordSerializer, UserSerializer
from .models import User


class ValidateQueryParams(serializers.Serializer):
    search = fields.RegexField(
        "^[0-9]{3,30}$",
        required=False
    )


class UsersViewSet(ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.filter(Q(is_superuser=False) | Q(is_staff=False))

        search_val = self.request.query_params.get('search')
        if search_val:
            queryset = User.objects.search(search_val)
        return queryset.order_by('pk')

    @action(detail=False, methods=['get'])
    def fix_register(self, request):
        for u in User.objects.all():
            y = Subscription.objects.filter(user=u).order_by('-section_year__year').values('section_year__year').first()
            if y:
                u.date_registered = datetime(y['section_year__year'], 1, 1)
                u.save()
        return Response({"status": "done"})

    @action(detail=True, methods=['get'])
    def paymenthistory(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        year = request.query_params.get('year')
        section = request.query_params.get('section')
        user_sections = Subscription.objects.filter(user=user).order_by('date_created')
        if year and section:
            payment_found = get_object_or_404(user_sections, section_year__year=year, section_year__section=section)
            serializer = UserPaymentSerializer(payment_found)
            return Response(serializer.data)
        else:
            serializer = UserPaymentSerializer(user_sections, many=True)
            return Response(serializer.data)

    @action(detail=True, methods=['post'], serializer_class=HistorySerializer)
    def changesection(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user_sectionhistory = History.objects.filter(user=user).order_by('-date_changed')
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            if user_sectionhistory.last().section != serializer.validated_data['section']:
                History(section=serializer.validated_data['section'], user=user, date_changed=datetime.now()).save()
                return Response({'message': 'User section changed successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'User already in this section'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=True, methods=['get', 'put', 'patch'], serializer_class=HistorySerializer)
    def sectionhistory(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if request.method == 'GET':
            user_sectionhistory = History.objects.filter(user=user).order_by('date_changed')
            serializer = self.serializer_class(user_sectionhistory, many=True)
            return Response(serializer.data)
        elif request.method == "PUT":
            return Response({})
        elif request.method == "PATCH":
            return Response({})

    @action(detail=True, methods=['GET'])
    def currentsection(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        last_change = History.objects.filter(user=user).order_by('-date_changed').first()
        return Response(HistorySerializer(last_change).data)


class UserViewSet(ViewSet):
    @action(detail=False, methods=['put'])
    def changepassword(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        user = self.request.user
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['currentPassword']):
                raise serializers.ValidationError("Incorrect old password")
            user.set_password(serializer.validated_data['newPassword'])
            user.save()
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=400)
