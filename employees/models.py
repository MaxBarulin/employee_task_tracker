from django.db import models


class Employee(models.Model):
    """
    Модель, представляющая сотрудника компании.
    Хранит основную информацию о сотруднике
    """

    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    position = models.CharField(max_length=150, verbose_name="Должность")

    def __str__(self):
        """
        Возвращает строковое представление объекта — ФИО сотрудника.
        Это используется, например, в админ-панели Django
        """
        return self.full_name

    class Meta:
        # Задаю человекочитаемые имена для модели в единственном и множественном числе
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
