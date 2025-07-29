from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tasks.models import Task, TaskStatus

from .models import Employee


class TestEmployeeAPI(APITestCase):
    """
    Набор тестов для API, связанного с сотрудниками.
    """

    # Метод setUp вызывается автоматически ПЕРЕД каждым тестом в этом классе.
    # Идеальное место для создания повторяющихся тестовых данных.
    def setUp(self):
        """Создает начальные данные для тестов."""
        # Создаем сотрудников
        self.ivanov = Employee.objects.create(
            full_name="Иванов", position="Разработчик"
        )
        self.petrov = Employee.objects.create(
            full_name="Петров", position="Тестировщик"
        )
        self.sidorov = Employee.objects.create(full_name="Сидоров", position="Аналитик")

        # Создаем задачи, чтобы проверить эндпоинт "busy-employees"
        # У Петрова будет 2 активные задачи
        Task.objects.create(
            name="Task 1 for Petrov",
            assignee=self.petrov,
            status=TaskStatus.IN_PROGRESS,
            deadline="2025-10-10",
        )
        Task.objects.create(
            name="Task 2 for Petrov",
            assignee=self.petrov,
            status=TaskStatus.IN_PROGRESS,
            deadline="2025-10-11",
        )
        # У Сидорова - 1 активная задача
        Task.objects.create(
            name="Task 1 for Sidorov",
            assignee=self.sidorov,
            status=TaskStatus.IN_PROGRESS,
            deadline="2025-10-12",
        )
        # У Иванова - 0 активных задач (но одна выполненная, чтобы проверить, что она не считается)
        Task.objects.create(
            name="Done task for Ivanov",
            assignee=self.ivanov,
            status=TaskStatus.DONE,
            deadline="2025-10-13",
        )

    def test_create_employee(self):
        """
        Проверяет успешное создание нового сотрудника через API.
        """
        # reverse() помогает получить URL по его имени из urls.py
        url = reverse("employee-list")
        data = {"full_name": "Новый Сотрудник", "position": "Стажер"}

        # self.client - это виртуальный HTTP-клиент
        response = self.client.post(url, data, format="json")

        # Проверяем, что ответ имеет статус 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Проверяем, что в базе данных теперь 4 сотрудника (3 из setUp + 1 новый)
        self.assertEqual(Employee.objects.count(), 4)
        # Проверяем, что данные нового сотрудника соответствуют отправленным
        self.assertEqual(response.data["full_name"], "Новый Сотрудник")

    def test_list_employees(self):
        """
        Проверяет получение списка сотрудников.
        """
        url = reverse("employee-list")
        response = self.client.get(url, format="json")

        # Проверяем, что ответ успешный (200 OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что в ответе 3 сотрудника, созданных в setUp
        self.assertEqual(len(response.data), 3)

    def test_busy_employees_endpoint_order(self):
        """
        Проверяет правильность работы эндпоинта "Занятые сотрудники",
        в частности, корректность сортировки.
        """
        # DRF именует кастомные actions как 'basename-action_name'
        url = reverse("employee-busy-employees")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что в ответе 3 сотрудника
        self.assertEqual(len(response.data), 3)
        employee_names_in_order = [emp["full_name"] for emp in response.data]

        expected_order = ["Петров", "Сидоров", "Иванов"]
        self.assertEqual(employee_names_in_order, expected_order)
