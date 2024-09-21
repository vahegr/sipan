import uuid
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import User


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


class UserSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=None, allow_empty_file=True, allow_null=True, required=False)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'national_code', 'first_name',
            'last_name', 'first_name_fa', 'last_name_fa',
            'email', 'address', 'phone', 'home', 'image',
            'date_registered'
        )
        read_only_fields = ('username', )

    def create(self, validated_data):
        if 'username' not in validated_data:
            last_id = User.objects.last().pk
            last_id += 1
            validated_data['username'] = uuid.uuid4().hex[:16]
        if 'national_code' in validated_data and len(validated_data['national_code']) < 10:
            validated_data['national_code'] = None
        return super().create(validated_data)
