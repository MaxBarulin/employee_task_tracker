from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from tasks.models import TaskStatus
from .models import Employee
# Теперь нам нужен только один главный сериализатор
from .serializers import EmployeeSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления сотрудниками.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    @action(detail=False, methods=['get'], url_path='busy-employees')
    def busy_employees(self, request):
        """
        Возвращает список сотрудников и их задачи, отсортированный
        по количеству активных задач.
        """
        active_tasks_filter = Q(tasks__status=TaskStatus.IN_PROGRESS)

        employees = Employee.objects.annotate(
            active_task_count=Count('tasks', filter=active_tasks_filter)
        # КРИТИЧЕСКИ ВАЖНАЯ ОПТИМИЗАЦИЯ:
        # .prefetch_related('tasks') говорит Django заранее загрузить все задачи
        # для всех найденных сотрудников одним дополнительным запросом.
        # Без этого для каждого сотрудника будет сделан отдельный запрос
        # в базу за его задачами (проблема "N+1").
        ).prefetch_related('tasks').order_by('-active_task_count')

        serializer = self.get_serializer(employees, many=True)
        return Response(serializer.data)
