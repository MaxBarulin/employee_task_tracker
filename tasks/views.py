from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from employees.models import Employee

from .models import Task, TaskStatus
from .serializers import ImportantTaskSerializer, TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD-операций с задачами
    Содержит кастомный эндпоинт для поиска "важных задач"
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @action(detail=False, methods=["get"], url_path="important-tasks")
    def important_tasks(self, request):
        """
        Реализует сложную бизнес-логику для поиска "важных" задач
        1. Находит задачи со статусом 'todo', блокирующие задачи со статусом 'in_progress'
        2. Подбирает для них подходящих исполнителей по заданным критериям.
        3. Возвращает результат в формате {Задача, Срок, [ФИО сотрудников]}.
        """
        # Шаг 1: Нахожу "важные" задачи, как они определены в ТЗ
        important_tasks = Task.objects.filter(
            status=TaskStatus.TODO, children__status=TaskStatus.IN_PROGRESS
        ).distinct()

        # Шаг 2: Нахожу наименее загруженного сотрудника. Это мой "эталон" для сравнения
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

        # Шаг 3: Для каждой важной задачи формирую список подходящих исполнителей
        result_data = []
        for task in important_tasks:
            # Использую set для автоматического исключения дубликатов
            suitable_employees = set()
            # Критерий А: Наименее загруженный сотрудник подходит всегда
            suitable_employees.add(least_busy_employee.full_name)

            # Критерий Б: Исполнители дочерних задач, если они не сильно перегружены
            # Для корректного подсчета их полной загрузки я разделяю логику на 2 запроса
            # 1. Сначала нахожу ID исполнителей активных дочерних задач
            child_assignee_ids = (
                Employee.objects.filter(
                    tasks__parent=task, tasks__status=TaskStatus.IN_PROGRESS
                )
                .values_list("id", flat=True)
                .distinct()
            )

            # 2. Если такие исполнители есть, делаю НОВЫЙ запрос, чтобы получить их реальную ПОЛНУЮ загрузку
            if child_assignee_ids:
                child_assignees_with_load = Employee.objects.filter(
                    id__in=child_assignee_ids
                ).annotate(
                    active_tasks_count=Count(
                        "tasks", filter=Q(tasks__status=TaskStatus.IN_PROGRESS)
                    )
                )

                # 3. Теперь проверяю условие с правильными данными о нагрузке
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
        # Так как я сам формирую данные для вывода, я передаю их в 'instance'
        # Вызов is_valid() здесь не нужен и привел бы к ошибке
        serializer = ImportantTaskSerializer(instance=result_data, many=True)
        return Response(serializer.data)
