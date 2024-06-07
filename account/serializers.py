from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import User
from subscription.models import Subscription


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
    subs = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'national_code', 'first_name', 'last_name', 'first_name_fa', 'last_name_fa', 'email', 'address', 'phone', 'home', 'subs', 'image')

    def get_subs(self, obj):
        user = get_object_or_404(User, pk=obj.pk)
        user_sections = Subscription.objects.filter(user=user).values_list("year__year", "year__section__name")
        user_section_subs = [f"{u[1]} {u[0]}" for u in user_sections]
        return user_section_subs
# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'phone', 'password', 'full_name', 'years', 'field')
#         extra_kwargs = {'password': {'write_only': True}}
#
#     def create(self, validated_data):
#         user = User(
#             email=validated_data['email'],
#             username=validated_data['username']
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         return user
