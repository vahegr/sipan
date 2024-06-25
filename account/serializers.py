import uuid
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import User
from subscription.models import History, Subscription


class ChangePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(write_only=True)
    newPassword = serializers.CharField(write_only=True)
    confirmPassword = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs.get('newPassword')
        confirm_password = attrs.get('confirmPassword')
        if password != confirm_password:
            raise serializers.ValidationError("Passwords don't match")
        return attrs


class UserPaymentSerializer(serializers.Serializer):
    payment_date = serializers.DateField(format="%Y-%m-%d")
    name = serializers.CharField()
    amount = serializers.IntegerField()


class UserSerializer(serializers.ModelSerializer):
    subs = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'national_code', 'first_name', 'last_name', 'first_name_fa', 'last_name_fa', 'section', 'email', 'address', 'phone', 'home', 'subs', 'image')
        read_only_fields = ('username', )

    def create(self, validated_data):
        if 'username' not in validated_data:
            last_id = User.objects.last().pk
            last_id += 1
            validated_data['username'] = uuid.uuid4().hex[:16]
        if 'national_code' in validated_data and len(validated_data['national_code']) < 10:
            validated_data['national_code'] = None
        return super().create(validated_data)

    def get_subs(self, obj):
        user = get_object_or_404(User, pk=obj.pk)
        user_sections = Subscription.objects.filter(user=user).values_list("year__year", "year__section__name")
        user_section_subs = [f"{u[1]} {u[0]}" for u in user_sections]
        return user_section_subs

    def get_section(self, obj):
        user = get_object_or_404(User, pk=obj.pk)
        user_sectionhistory = History.objects.filter(user=user).last()
        return user_sectionhistory.section.name if user_sectionhistory is not None else ""
