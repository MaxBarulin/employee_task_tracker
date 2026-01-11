from rest_framework import serializers

from tasks.serializers import TaskSerializer

from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Employee
    Включает вложенный список всех задач сотрудника для соответствия
    требованиям ТЗ по эндпоинту "Занятые сотрудники"
    """

    # Это поле будет содержать список задач, отформатированных
    # с помощью TaskSerializer. Оно будет доступно только для чтения
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        # Добавляем 'tasks' в список полей для вывода
        fields = ("id", "full_name", "position", "tasks")
