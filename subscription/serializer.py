from django.shortcuts import get_object_or_404
from rest_framework import serializers

from account.models import User
from .models import History, SectionYear, Subscription, Section
from account.serializers import UserSerializer


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


class UserSectionPaymentSerializer(serializers.Serializer):
    force = serializers.BooleanField(required=False, write_only=True)
    amount = serializers.IntegerField()
    user = serializers.SerializerMethodField()

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)
        internal_data['user'] = User.objects.get(pk=data['user'])
        return internal_data


class UserPaymentSerializer(serializers.ModelSerializer):
    force = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'date_created', 'amount', 'section_year', 'force')
        read_only_fields = ('id', )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['section_year'] = SectionYearSerializer(SectionYear.objects.get(pk=ret['section_year'])).data
        return ret


class SubscriptionSerializer(serializers.ModelSerializer):
    national_code = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'section_year', 'national_code', 'date_created', 'amount')

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)

        if 'national_code' in data:
            if len(data['national_code']) == 10:
                internal_data['user'] = get_object_or_404(User, national_code=data['national_code']).id
            del internal_data['national_code']

        if 'section' in data and 'year' in data:
            section_year = get_object_or_404(SectionYear, section=int(data['section']), year=int(data['year']))
            del internal_data['section']
            del internal_data['year']
            internal_data['year'] = section_year.pk

        return internal_data


class SectionMemberSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField()
    has_paid = serializers.BooleanField()
    payment = serializers.IntegerField()
    section = serializers.IntegerField()
    amount = serializers.IntegerField()

    def get_user(self, obj):
        return UserSerializer(obj, context={'request': self.context.get('request')}).data


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


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ('id', 'date_changed', 'user', 'section')
        read_only_fields = ('id', )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['section_name'] = instance.section.name
        ret['section'] = SectionSerializer(instance.section).data
        return ret


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'name', 'color')


class SectionChartSerializer(serializers.ModelSerializer):
    years = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ('id', 'name', 'color', 'years')

    def get_years(self, obj):
        years = SectionYear.objects.filter(section=obj.pk)
        return {x for x in SectionYearSerializer(years, many=True).data}


class SectionYearSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    payed_count = serializers.SerializerMethodField()

    class Meta:
        model = SectionYear
        fields = ('id', 'section', 'year', 'price', 'count', 'payed_count')

    def update(self, instance, validated_data):
        validated_data.pop('section', None)
        validated_data.pop('year', None)
        return super().update(instance, validated_data)

    def to_internal_value(self, data):
        return super().to_internal_value(data)

    def get_count(self, obj):
        return User.objects.in_section(obj.section.pk, obj.year).count()

    def get_payed_count(self, obj):
        return User.objects.in_section(obj.section.pk, obj.year, payment=True).filter(has_paid=True).count()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['section'] = SectionSerializer(Section.objects.get(pk=ret['section'])).data
        return ret


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

        if not User.objects.in_section(section_id, year_obj.year).get(pk=user_id):
            raise serializers.ValidationError({'user': 'User doesn\'nt belong to this section'})
        return internal_data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['section'] = SectionSerializer(instance.section).data
        ret['year'] = SectionYearSerializer(SectionYear.objects.get(section=ret['section'], year=instance.year)).data
        return ret
