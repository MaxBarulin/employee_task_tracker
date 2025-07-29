from datetime import date

from rest_framework import serializers

# 1. ИСПРАВЛЕНИЕ: Импортируем и Task, и TaskStatus
from .models import Task, TaskStatus


class TaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Task.
    Включает в себя CRUD операции и кастомную валидацию.
    """

    class Meta:
        model = Task
        fields = ("id", "name", "parent", "assignee", "status", "deadline")

    def validate_deadline(self, value):
        """
        Проверяет, что дедлайн задачи не находится в прошлом.
        """
        if self.instance and self.instance.deadline == value:
            return value

        if value < date.today():
            raise serializers.ValidationError("Дедлайн не может быть в прошлом.")
        return value

    def validate(self, data):
        """
        Метод для валидации, затрагивающей несколько полей.
        """
        parent_task = data.get("parent")
        deadline = data.get("deadline")
        status = data.get("status")
        assignee = data.get("assignee")

        if parent_task and deadline:
            if deadline > parent_task.deadline:
                raise serializers.ValidationError(
                    {
                        "deadline": "Дедлайн дочерней задачи не может быть позже дедлайна родительской."
                    }
                )

        current_assignee = assignee or (self.instance and self.instance.assignee)

        # 2. ИСПРАВЛЕНИЕ: Обращаемся к TaskStatus напрямую
        if status == TaskStatus.DONE and not current_assignee:
            raise serializers.ValidationError(
                {"status": "Нельзя завершить задачу, у которой нет исполнителя."}
            )

        return data


class ImportantTaskSerializer(serializers.Serializer):
    """
    Сериализатор для специального эндпоинта "Важные задачи".
    Используется только для вывода данных (read-only).
    """

    task_name = serializers.CharField(read_only=True)
    deadline = serializers.DateField(read_only=True)
    suitable_employees = serializers.ListField(
        child=serializers.CharField(), read_only=True
    )
