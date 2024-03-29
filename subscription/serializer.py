from django.shortcuts import get_object_or_404
from rest_framework import serializers

from account.models import User
from .models import SectionYear, Subscription, Section
from account.serializers import UserSerializer


class SubscriptionSerializer(serializers.ModelSerializer):
    national_code = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'year', 'national_code')

    def to_internal_value(self, data):
        new_data = data.copy()
        if 'national_code' in data:
            if len(data['national_code']) == 10:
                new_data['user'] = get_object_or_404(User, national_code=data['national_code']).id
                
            del new_data['national_code']
        if 'section' in data and 'year' in data:
            section_year = get_object_or_404(SectionYear, section=int(data['section']), year=int(data['year']))
            del new_data['section']
            del new_data['year']
            new_data['year'] = section_year.pk

        return super().to_internal_value(new_data)

    
class SectionSubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('id', 'year', 'user')

    def get_user(self, obj):
        return UserSerializer(obj.user).data


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'name')


class SectionYearSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    class Meta:
        model = SectionYear
        fields = ('id', 'section', 'year', 'price', 'count')

    def get_count(self, obj):
        subscriptions = Subscription.objects.filter(year=obj.pk)
        return subscriptions.count()