from datetime import datetime
from django.db.models import CharField
from django.shortcuts import get_object_or_404
from django.db.models import Q, F
from django.db.models.functions import Concat
from django.db.models import Value

from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework import fields, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from subscription.serializer import HistorySerializer, SectionSerializer

from .serializers import ChangePasswordSerializer, UserSerializer, UserPaymentSerializer
from .models import User
from subscription.models import History, Subscription

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
    def paymenthistory(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        # user_sections = Subscription.objects.filter(user=user).values_list("year__year", "year__section__name", "amount", named=True)
        user_sections = Subscription.objects.filter(user=user, amount__gt=0).annotate(payment_date=F("date_created"), name=Concat(F("year__section__name"), Value(" "), F("year__year"), output_field=CharField()))
        serializer = UserPaymentSerializer(user_sections, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], serializer_class=HistorySerializer)
    def changesection(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user_sectionhistory = History.objects.filter(user=user).order_by('-date_changed')
        serializer = HistorySerializer(data=request.data)
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
