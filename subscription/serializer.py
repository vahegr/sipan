from django.shortcuts import get_object_or_404
from rest_framework import serializers

from account.models import User
from .models import History, SectionYear, Subscription, Section
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


# class ChangeSectionSerializer(serializers.Serializer):
#     national_code = serializers.CharField(required=False, write_only=True)
#     user = serializers.IntegerField(write_only=True)
#     section = serializers.IntegerField(write_only=True)

#     def to_internal_value(self, data):
#         new_data = data.copy()
#         if 'national_code' in data:
#             if len(data['national_code']) == 10:
#                 new_data['user'] = get_object_or_404(User, national_code=data['national_code']).id
#             del new_data['national_code']
#         if 'section' in data:
#             section = get_object_or_404(Section, section=int(data['section']))
#             new_data['section'] = section
#         return super().to_internal_value(new_data)


class SectionSubscriptionSerializerNew(serializers.Serializer):
    user = serializers.SerializerMethodField()
    has_paid = serializers.BooleanField()
    payment = serializers.IntegerField()
    section = serializers.IntegerField()
    amount = serializers.IntegerField()

    def get_user(self, obj):
        return UserSerializer(obj, context={'request': self.context.get('request')}).data


class SectionSubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), pk_field='user')

    class Meta:
        model = Subscription
        fields = ('id', 'year', 'user')

    # def get_user(self, obj):
    #     return UserSerializer(obj.user, context={'request': self.context.get('request')}).data


class SectionYearPay(serializers.Serializer):
    user = serializers.IntegerField()


class UserIDSerializer(serializers.Serializer):
    user = serializers.IntegerField()

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)
        user_id = data.get('user')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                internal_data['user'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError({'user': 'Invalid user ID'})
        return internal_data

    def to_representation(self, instance):
        return UserSerializer(User.objects.get(pk=instance['user'])).data


class ChangeSectionSerializer(UserIDSerializer):
    date_changed = serializers.DateField(required=False)


class UserNationalCodeSerializer(serializers.Serializer):
    national_code = serializers.CharField()

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)
        national_code = data.get('national_code')
        if national_code:
            try:
                user = User.objects.filter(national_code=national_code).first()
                internal_data['user'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError({'user': 'Invalid user ID'})
        return internal_data


class UserPaymentSerializer(UserIDSerializer):
    amount = serializers.IntegerField()
    force = serializers.BooleanField(required=False)
    date_created = serializers.DateField(required=False)


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ('id', 'date_changed', 'user', 'section')
        read_only_fields = ('date_changed', )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['section_name'] = instance.section.name
        return ret


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'name', 'color')


class SectionYearSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    class Meta:
        model = SectionYear
        fields = ('id', 'section', 'year', 'price', 'count')

    def update(self, instance, validated_data):
        validated_data.pop('section', None)
        validated_data.pop('year', None)
        return super().update(instance, validated_data)

    def get_count(self, obj):
        return len(obj.get_members())


class BulkPrintSerializer(serializers.Serializer):
    section = serializers.PrimaryKeyRelatedField(queryset=Section.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    year = serializers.IntegerField()

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)
        section_id = data.get('section')
        user_id = data.get('user')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                internal_data['user'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError({'user': 'Invalid user ID'})

        if section_id:
            try:
                section = Section.objects.get(id=section_id)
                internal_data['section'] = section
            except Section.DoesNotExist:
                raise serializers.ValidationError({'section': 'Invalid section ID'})

        year = data.get('year')
        if year:
            try:
                year_obj = SectionYear.objects.get(year=year, section=section_id)
                internal_data['year'] = year_obj
            except SectionYear.DoesNotExist:
                raise serializers.ValidationError({'year': 'Invalid year'})

        if not internal_data['year'].get_members().filter(pk=user_id):
            raise serializers.ValidationError({'user': 'User doesn\'n belong to this section year'})
        return internal_data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['section'] = SectionSerializer(instance.section).data
        ret['year'] = SectionYearSerializer(SectionYear.objects.get(section=ret['section'], year=instance.year)).data
        return ret