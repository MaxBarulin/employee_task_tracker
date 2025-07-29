from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from employees.models import Employee

from .models import Task, TaskStatus
from .serializers import ImportantTaskSerializer, TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления задачами.
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @action(detail=False, methods=["get"], url_path="important-tasks")
    def important_tasks(self, request):
        """
        Возвращает задачи, не взятые в работу, от которых зависят другие
        задачи, взятые в работу. Также предлагает сотрудников для их выполнения.
        """
        important_tasks = Task.objects.filter(
            status=TaskStatus.TODO, children__status=TaskStatus.IN_PROGRESS
        ).distinct()

        employees_load = Employee.objects.annotate(
            active_tasks_count=Count(
                "tasks", filter=Q(tasks__status=TaskStatus.IN_PROGRESS)
            )
        ).order_by("active_tasks_count")

        if not employees_load.exists():
            return Response(
                {"message": "В системе нет сотрудников для назначения задач."},
                status=404,
            )

        least_busy_employee = employees_load.first()
        min_tasks_count = least_busy_employee.active_tasks_count

        result_data = []
        for task in important_tasks:
            suitable_employees = set()
            suitable_employees.add(least_busy_employee.full_name)

            # --- ИСПРАВЛЕННЫЙ БЛОК ЛОГИКИ ---

            # Шаг 1: Находим ID исполнителей активных дочерних задач.
            child_assignee_ids = (
                Employee.objects.filter(
                    tasks__parent=task, tasks__status=TaskStatus.IN_PROGRESS
                )
                .values_list("id", flat=True)
                .distinct()
            )

            # Шаг 2: Если такие исполнители есть, делаем НОВЫЙ запрос,
            # чтобы получить их реальную полную загрузку.
            if child_assignee_ids:
                child_assignees_with_load = Employee.objects.filter(
                    id__in=child_assignee_ids
                ).annotate(
                    active_tasks_count=Count(
                        "tasks", filter=Q(tasks__status=TaskStatus.IN_PROGRESS)
                    )
                )

                # Шаг 3: Теперь проверяем условие с правильными данными.
                for assignee in child_assignees_with_load:
                    if assignee.active_tasks_count <= min_tasks_count + 2:
                        suitable_employees.add(assignee.full_name)

            result_data.append(
                {
                    "task_name": task.name,
                    "deadline": task.deadline,
                    "suitable_employees": list(suitable_employees),
                }
            )

        serializer = ImportantTaskSerializer(instance=result_data, many=True)
        return Response(serializer.data)
