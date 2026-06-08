from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from rest_framework import serializers

from accounts.models import User, ClassName, ClassStudent
from accounts.models.user import USER_ROLE


class ClassStudentSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='student')
    class_id = serializers.PrimaryKeyRelatedField(queryset=ClassName.objects.all(), source='class_name')

    class Meta:
        model = ClassStudent
        fields = ['student_id', 'class_id']

class AddStudentToClass(APIView):

    def post(self, request):
        student_id = request.data.get('student_id')
        class_id = request.data.get('class_id')

        if not student_id or not class_id:
            return Response({'error': 'Cả student_id và class_id đều là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = User.objects.get(id=student_id)
            if student.role != USER_ROLE.STUDENT:
                return Response({'error': 'Chỉ có thể thêm tài khoản học sinh vào lớp'}, status=status.HTTP_400_BAD_REQUEST)

            existing_class = ClassStudent.objects.filter(student_id=student_id).first()
            if existing_class:
                return Response({'error': 'Học sinh này đã được phân vào một lớp khác'},
                                status=status.HTTP_400_BAD_REQUEST)

            class_obj = ClassName.objects.get(id=class_id)
            if class_obj.number_of_students >= 40:
                return Response({'error': 'Lớp này đã đủ số học sinh'}, status=status.HTTP_400_BAD_REQUEST)

            class_student = ClassStudent.objects.create(student_id=student_id, class_name_id=class_id)

            class_obj.number_of_students += 1
            class_obj.save()

            return Response({'success': True, 'data': ClassStudentSerializer(class_student).data},
                            status=status.HTTP_201_CREATED)
        except ClassName.DoesNotExist:
            return Response({'error': 'Mã lớp không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'Mã học sinh không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
