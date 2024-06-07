import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, serializers, mixins
from rest_framework.decorators import action

from account.models import User
from sipan.card_generator import generate_card, generate_page
from sipan.excel_report import generate_excel_report
from .serializer import SectionSubscriptionSerializer, SubscriptionSerializer, SectionSerializer, SectionYearSerializer
from .models import Subscription, Section, SectionYear
from sipan.settings import BASE_DIR


class UserSubsViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    # def retrieve(self, request, pk=None):
    #     data = get_object_or_404(self.queryset, pk=pk)
    #     serializer = self.serializer_class(data, many=True)
    #     return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def card(self, request, pk):
        sub = get_object_or_404(self.queryset, pk=pk)
        img_bytes = generate_card(sub)
        return HttpResponse(img_bytes, content_type="image/jpeg")

    @action(detail=False, methods=['post'])
    def cards(self, request):
        pdf_bytes = generate_page(list(request.data['subs']))
        return HttpResponse(pdf_bytes, content_type="application/pdf")

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

    def list(self, request, *args, **kwargs):
        section = request.query_params.get('section', None)
        if section:
            section_id = int(section)
            section_obj = get_object_or_404(Section, pk=section_id)
            filtered_years = SectionYear.objects.filter(section=section_obj)
            serializer = self.serializer_class(filtered_years, many=True)
            return Response(serializer.data)
        else:
            return super().list(request, args, kwargs)


class SectionViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    pagination_class = None


    def retrieve(self, request, pk=None):
        section_obj = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(section_obj)

        year = request.query_params.get('year', None)
        if year:
            year = int(year)
            year_obj = SectionYear.objects.filter(
                year=year, section=section_obj).first()

            subscriptions = Subscription.objects.filter(
                year=year_obj.pk).order_by('-id').all()
            paginator = PageNumberPagination()

            page = paginator.paginate_queryset(subscriptions, request)

            subscriptions_serializer = SectionSubscriptionSerializer(
                page, many=True, context={'request': request})
            
            result = []
            for d in subscriptions_serializer.data:
                temp_dict = {k: v for k, v in d.items() if k not in ['section', 'year']}
                temp_dict.update({'year': year})
                temp_dict.update({'sectionName': section_obj.name})
                result.append(temp_dict)

            return Response({
                **serializer.data,
                "count": len(subscriptions),
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": result
            })
        else:
            section_years = SectionYear.objects.filter(
                section=section_obj).order_by('-year')
            section_serializer = SectionYearSerializer(
                section_years, many=True, context={'request': request})
            return Response({
                **serializer.data,
                "years": [{k: v for k, v in d.items() if k not in ['section']} for d in section_serializer.data]
            })
