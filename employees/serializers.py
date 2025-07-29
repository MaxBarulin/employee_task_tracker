from rest_framework import serializers

from tasks.serializers import TaskSerializer

from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Employee, который включает
    вложенный список всех задач сотрудника.
    """

    # Поле будет содержать список задач, отформатированных с помощью TaskSerializer.
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        # Добавляем 'tasks' в список полей для вывода.
        fields = ("id", "full_name", "position", "tasks")
