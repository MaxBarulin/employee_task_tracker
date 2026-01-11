from datetime import date

from rest_framework import serializers

# 1. ИСПРАВЛЕНИЕ: Импортируем и Task, и TaskStatus
from .models import Task, TaskStatus


class TaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Task
    Включает в себя CRUD операции и кастомную бизнес-логику для валидации данных
    """

    class Meta:
        model = Task
        fields = ("id", "name", "parent", "assignee", "status", "deadline")

    def validate_deadline(self, value):
        """
        Проверяет, что дедлайн задачи не находится в прошлом
        """
        # self.instance - это объект, который обновляется (None при создании).
        # Эта проверка позволяет редактировать старые задачи с прошедшим дедлайном,
        # но не создавать новые или переносить существующие в прошлое
        if self.instance and self.instance.deadline == value:
            return value

        if value < date.today():
            raise serializers.ValidationError("Дедлайн не может быть в прошлом.")
        return value

    def validate(self, data):
        """
        Метод для сложной валидации, затрагивающей несколько полей
        1. Проверяет, что у дочерней задачи дедлайн не позже родительской
        2. Проверяет, что у задачи со статусом "Выполнено" есть исполнитель
        """
        parent_task = data.get("parent")
        deadline = data.get("deadline")
        status = data.get("status")
        assignee = data.get("assignee")

        # Проверка 1: Дедлайн дочерней задачи
        if parent_task and deadline:
            if deadline > parent_task.deadline:
                raise serializers.ValidationError(
                    {
                        "deadline": "Дедлайн дочерней задачи не может быть позже дедлайна родительской."
                    }
                )
        # Проверка 2: Статус "Выполнено"
        # Логика для получения текущего исполнителя как при создании, так и при обновлении
        current_assignee = assignee or (self.instance and self.instance.assignee)

        # Обращаемся к TaskStatus напрямую
        if status == TaskStatus.DONE and not current_assignee:
            raise serializers.ValidationError(
                {"status": "Нельзя завершить задачу, у которой нет исполнителя."}
            )

        return data


class ImportantTaskSerializer(serializers.Serializer):
    """
    Сериализатор для специального эндпоинта "Важные задачи"
    Используется только для вывода данных (read-only), поэтому не является ModelSerializer
    """

    task_name = serializers.CharField(read_only=True)
    deadline = serializers.DateField(read_only=True)
    suitable_employees = serializers.ListField(
        child=serializers.CharField(), read_only=True
    )
