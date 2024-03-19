from rest_framework import serializers
from .models import Subscription, SubSection


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'sub', 'year', 'user')

class SubSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubSection
        fields = ('id', 'name')
