from django.db import models

from employees.models import Employee


class TaskStatus(models.TextChoices):
    """
    Класс для определения возможных статусов задачи
    Использование TextChoices делает код более читаемым и надежным,
    избегая "магических строк" в коде
    """

    TODO = "todo", "К выполнению"
    IN_PROGRESS = "in_progress", "В работе"
    DONE = "done", "Выполнено"
    CANCELED = "canceled", "Отменено"


class Task(models.Model):
    """
    Модель, представляющая задачу в трекере
    Может быть связана с сотрудником и иметь родительскую задачу
    """

    name = models.CharField(max_length=255, verbose_name="Наименование задачи")
    # Связь "сам с собой" для реализации иерархии задач
    parent = models.ForeignKey(
        "self",
        # Если родительскую задачу удалят, это поле станет NULL
        on_delete=models.SET_NULL,
        # Поле может быть пустым в базе данных
        null=True,
        # Поле не является обязательным для заполнения в формах
        blank=True,
        # Ключевое поле! Позволяет обращаться к дочерним задачам (task.children.all())
        related_name="children",
        verbose_name="Родительская задача",
    )
    # Связь с исполнителем задачи
    assignee = models.ForeignKey(
        Employee,
        # Если сотрудника удалят, задача останется, но без исполнителя
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        # Ключевое поле! Позволяет обращаться к задачам сотрудника (employee.tasks.all())
        related_name="tasks",
        verbose_name="Исполнитель",
    )
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        # По умолчанию любая новая задача имеет статус "К выполнению".
        default=TaskStatus.TODO,
        verbose_name="Статус",
    )
    deadline = models.DateField(verbose_name="Срок выполнения")

    def __str__(self):
        """
        Возвращает строковое представление — наименование задачи
        """
        return self.name

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
