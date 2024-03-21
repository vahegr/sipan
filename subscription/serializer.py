from rest_framework import serializers
from .models import Subscription, Section
from account.serializers import UserSerializer


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'section', 'user', 'year')


class SectionSubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('id', 'section', 'year', 'user')

    def get_user(self, obj):
        return UserSerializer(obj.user).data


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'name')
