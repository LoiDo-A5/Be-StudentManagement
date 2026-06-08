from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from accounts.models import User, StudentScore, ClassStudent
from rest_framework.filters import SearchFilter
import django_filters
from django_filters import rest_framework as filters


class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        data_response = {
            'page_size': self.page_size,
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        }
        return Response(data_response)


class StudentScoreSerializer(serializers.ModelSerializer):
    semester_1_avg = serializers.FloatField()
    semester_2_avg = serializers.FloatField()

    class Meta:
        model = StudentScore
        fields = ['semester_1_avg', 'semester_2_avg']


class UserListSerializer(serializers.ModelSerializer):
    student_score = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'gender', 'birthday', 'address', 'email', 'phone_number',
                  'is_phone_verified', 'avatar', 'time_zone', 'role', 'student_score', 'class_name')

    def get_student_score(self, obj):
        class_student = ClassStudent.objects.filter(student=obj).first()

        if class_student:
            student_score = StudentScore.objects.filter(student=obj, class_name=class_student.class_name).first()
            if student_score:
                return {
                    "semester_1_avg": student_score.semester_1_avg,
                    "semester_2_avg": student_score.semester_2_avg,
                }
        return None

    def get_class_name(self, obj):
        class_student = ClassStudent.objects.filter(student=obj).first()
        if class_student and class_student.class_name:
            class_name = f"{class_student.class_name.level.level_name}{class_student.class_name.class_name}"
            return class_name
        return 'Không có lớp'


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = UserPagination
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    search_fields = ['full_name']

    @action(detail=False, methods=['get'])
    def list_student(self, request):
        class_name_id = request.query_params.get('class_name_id', None)
        if class_name_id:
            students = User.objects.filter(classstudent__class_name__id=class_name_id).distinct()
        else:
            students = User.objects.filter(role=1)

        students = self.filter_queryset(students)

        page = self.paginate_queryset(students)
        if page is not None:
            serializer = UserListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserListSerializer(students, many=True)
        return Response(serializer.data)
