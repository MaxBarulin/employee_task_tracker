from django.db import models

from employees.models import Employee


class TaskStatus(models.TextChoices):
    TODO = "todo", "К выполнению"
    IN_PROGRESS = "in_progress", "В работе"
    DONE = "done", "Выполнено"
    CANCELED = "canceled", "Отменено"


class Task(models.Model):
    name = models.CharField(max_length=255, verbose_name="Наименование задачи")
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительская задача",
    )
    assignee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Исполнитель",
    )
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.TODO,
        verbose_name="Статус",
    )
    deadline = models.DateField(verbose_name="Срок выполнения")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
