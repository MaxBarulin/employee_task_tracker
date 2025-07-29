from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from employees.models import Employee

from .models import Task, TaskStatus


class TestTaskModel(TestCase):
    """
    Набор тестов для проверки самой модели Task.
    """

    def test_task_creation(self):
        """Проверяет, что модель задачи создается корректно в базе данных."""
        employee = Employee.objects.create(full_name="Тестовый", position="Тестировщик")
        task = Task.objects.create(
            name="Тестовая задача",
            assignee=employee,
            status=TaskStatus.TODO,
            deadline="2025-12-25",
        )
        self.assertEqual(task.name, "Тестовая задача")
        self.assertEqual(task.status, "todo")
        self.assertEqual(str(task), "Тестовая задача")


# Пример заготовки для тестов API задач, которые вам нужно будет написать
class TestTaskAPI(APITestCase):
    """
    Набор тестов для API, связанного с задачами.
    """

    def setUp(self):
        """Создает начальные данные для тестов API задач."""
        self.employee1 = Employee.objects.create(full_name="Работник 1", position="A")
        self.task1 = Task.objects.create(name="Простая задача", deadline="2025-11-11")

    def test_list_tasks(self):
        """Проверяет получение списка задач."""
        url = reverse("task-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # TODO: Написать тест для эндпоинта 'important-tasks'
    def test_important_tasks_endpoint(self):
        """
        Тест для эндпоинта "Важные задачи".
        Это самый важный тест, который вам нужно будет реализовать.
        """
        # 1. Создайте сложную ситуацию с данными в setUp (родительская задача, дочерняя, несколько сотрудников с
        # разной нагрузкой)
        # 2. Сделайте GET-запрос на reverse('task-important-tasks')
        # 3. Проверьте, что статус ответа 200 OK
        # 4. Проверьте, что в ответе правильное количество важных задач
        # 5. Проверьте, что для каждой важной задачи предложены правильные сотрудники
        self.skipTest("Тест для 'important-tasks' еще не реализован.")
