from django.utils.translation import gettext
from rest_framework import serializers
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from accounts.models import User, SystemSetting
from django.contrib.auth.hashers import make_password
from datetime import date
from accounts.models.user import USER_ROLE

class RegisterPhoneSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    full_name = serializers.CharField(max_length=100, required=True)
    gender = serializers.ChoiceField(choices=[(0, 'Male'), (1, 'Female')], required=True)
    birthday = serializers.DateField(required=True)
    address = serializers.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = (
            'full_name',
            'email',
            'password1',
            'password2',
            'gender',
            'birthday',
            'address',
            'time_zone',
        )

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(gettext('This email is already in use'))
        return email

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError(gettext("The two password fields didn't match."))

        attrs['password'] = make_password(attrs['password1'])
        return attrs

    def validate_time_zone(self, time_zone):
        if not time_zone:
            time_zone = 'Asia/Ho_Chi_Minh'
        return time_zone

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class RegisterPhoneApi(GenericAPIView):
    serializer_class = RegisterPhoneSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        system_setting = SystemSetting.objects.first()
        if not system_setting:
            system_setting = SystemSetting.objects.create(min_student_age=15, max_student_age=20)

        birthday = serializer.validated_data['birthday']
        today = date.today()
        age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

        if not (system_setting.min_student_age <= age <= system_setting.max_student_age):
            return Response(
                {'error': gettext(f'Độ tuổi không hợp lệ. Chỉ chấp nhận từ {system_setting.min_student_age}'
                                  f' đến {system_setting.max_student_age} tuổi.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        if User.objects.filter(email=email).exists():
            return Response({'error': gettext('Email already exists')}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.create(
            username=email,
            email=email,
            password=serializer.validated_data['password'],
            full_name=serializer.validated_data['full_name'],
            gender=serializer.validated_data['gender'],
            birthday=birthday,
            address=serializer.validated_data['address'],
            time_zone=serializer.validated_data.get('time_zone', 'Asia/Ho_Chi_Minh'),
            role=USER_ROLE.STUDENT,
        )

        return Response(
            {'message': gettext('Create user success')},
            status=status.HTTP_200_OK
        )
