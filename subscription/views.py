import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, serializers, mixins
from rest_framework.decorators import action

from account.serializers import UserSerializer
from sipan.card_generator import generate_card, generate_page
from sipan.excel_report import generate_excel_report
from .serializer import BulkPrintSerializer, ChangeSectionSerializer, HistorySerializer, SectionSubscriptionSerializer, SectionSubscriptionSerializerNew, SectionYearPay, SubscriptionSerializer, SectionSerializer, SectionYearSerializer, UserIDSerializer, UserNationalCodeSerializer, UserPaymentSerializer
from .models import History, Subscription, Section, SectionYear, User
from sipan.settings import BASE_DIR


class UserSubsViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    @action(detail=False, methods=['GET'])
    def excel_report(self, request):
        excel_report = generate_excel_report()
        now = datetime.datetime.now()

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="subscriptions_till_{now.strftime("%Y_%m_%d")}.xlsx"'
        response.write(excel_report)
        return response

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class SectionYearView(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):

    queryset = SectionYear.objects.all()
    serializer_class = SectionYearSerializer

    @action(methods=['get'], detail=False, url_path='section/(?P<section_id>\d+)')
    def section_years(self, request, section_id):
        section_obj = get_object_or_404(Section, pk=section_id)
        filtered_years = SectionYear.objects.filter(section=section_obj)
        serializer = self.serializer_class(filtered_years, many=True)
        return Response(serializer.data)
    


class SectionViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    pagination_class = None

    @action(methods=['get'], detail=True, url_path=r'year/(?P<year>\d+)')
    def year_info(self, request, year, pk=None):

        section_obj = get_object_or_404(self.queryset, pk=pk)
        year_obj = SectionYear.objects.filter(year=year, section=section_obj).first()

        search_val = request.query_params.get('search')
        year_members = year_obj.get_members(search_val)

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(year_members, request)

        subscriptions_serializer = SectionSubscriptionSerializerNew(page, many=True, context={'request': request})
        return Response({
            "count": len(year_members),
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": subscriptions_serializer.data
        })

    @action(methods=['post', 'delete'], detail=True, url_path=r'year/(?P<year>\d+)/pay', serializer_class=UserPaymentSerializer)
    def year_pay(self, request, year, pk=None):
        section_obj = get_object_or_404(self.queryset, pk=pk)
        year_obj = get_object_or_404(SectionYear.objects.all(), year=year, section=section_obj)
        year_members = year_obj.get_members()

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data['user']
        forced = serializer.validated_data['force'] if 'force' in serializer.validated_data.keys() else False
        date_created = serializer.validated_data['date_created'] if 'date_created' in serializer.validated_data.keys() else datetime.datetime.now()
        

        if not year_members.filter(pk=user_obj.id) and not forced:
            return Response({"message": "This member doesn't have the permission to be in this section-year"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if request.method == 'POST':
            if Subscription.objects.filter(user=user_obj, year=year_obj).first() is not None:
                s = Subscription.objects.filter(user=user_obj, year=year_obj).first()
                s.amount = serializer.validated_data['amount']
                s.save()
                return Response({"message": "User's record already exists and updated"}, status=status.HTTP_200_OK)
            Subscription(user=user_obj, year=year_obj, amount=serializer.validated_data['amount'], date_created=date_created).save()
            return Response({"message": f"User ({user_obj.id}) Subscription for section #{year_obj.section}-{year_obj.year} created successfully"}, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            subToRemove = Subscription.objects.filter(user=user_obj, year=year_obj).first()
            if subToRemove is None:
                return Response({"message": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)
            subToRemove.delete()

            return Response({"message": f"User ({user_obj.id}) Subscription for section #{year_obj.section}-{year_obj.year} removed"}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        section_obj = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(section_obj)

        section_years = SectionYear.objects.filter(
            section=section_obj).order_by('-year')
        section_serializer = SectionYearSerializer(
            section_years, many=True, context={'request': request})
        return Response({
            **serializer.data,
            "years": [{k: v for k, v in d.items() if k not in ['section']} for d in section_serializer.data]
        })

    @action(detail=True, methods=['get'], url_path=r'year/(?P<year>\d+)/card/(?P<user_id>\d+)')
    def card(self, request, user_id, year, pk):
        section_obj = get_object_or_404(self.queryset, pk=pk)
        section_year_obj = get_object_or_404(SectionYear.objects.filter(section=section_obj), year=year)
        user_obj = get_object_or_404(User, pk=user_id)
        img_bytes = generate_card(user_obj, section_year_obj)
        return HttpResponse(img_bytes, content_type="image/jpeg")

    @action(detail=False, methods=['post'], serializer_class=BulkPrintSerializer)
    def batchprint(self, request):
        serializer = self.serializer_class(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        pdf_bytes = generate_page(serializer.validated_data)
        return HttpResponse(pdf_bytes, content_type="application/pdf")

    @action(detail=True, methods=['post'], serializer_class=ChangeSectionSerializer)
    def changesection(self, request, pk):
        new_section_obj = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        last_history = History.objects.filter(user=serializer.validated_data['user']).order_by('-date_changed').first()
        # print(serializer.validated_data['date_changed'])
        if not last_history or last_history.section != new_section_obj:
            date_changed = datetime.datetime.now() if 'date_changed' not in serializer.validated_data.keys() else serializer.validated_data['date_changed']
            History(user=serializer.validated_data['user'], section=new_section_obj, date_changed=date_changed).save()
            return Response({"message": f"User section successfully changed to {new_section_obj}"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User already in this section"}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(methods=['get'], detail=True)
    def members(self, request, pk):
        section_obj = get_object_or_404(Section, pk=pk)
        section_members = section_obj.get_members()

        search_val = request.query_params.get('search')
        if search_val:
            section_members = section_members.filter(Q(national_code__icontains=search_val) | Q(first_name__icontains=search_val) | Q(last_name__icontains=search_val))

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(section_members, request)

        serializer = UserSerializer(page, many=True, context={'request': request})
        return Response({
            "count": len(section_members),
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": serializer.data
        })
