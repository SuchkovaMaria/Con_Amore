from datetime import timedelta

from django.db import models


class Table(models.Model):
    """Модель столика"""

    table_number = models.IntegerField(verbose_name="Номер столика", help_text="Введите номер столика")
    description = models.CharField(
        max_length=200, verbose_name="Описание", help_text="Добавьте описание", blank=True, null=True
    )

    # путь для сохранения фото столика
    image = models.ImageField(
        upload_to="data/image_table",
        blank=True,
        null=True,
        verbose_name="Фото столика",
        help_text="Загрузите фото столика",
    )
    number_of_guests = models.IntegerField(verbose_name="Количество гостей", help_text="Укажите количество гостей")

    class Meta:
        verbose_name = "Столик"
        verbose_name_plural = "Столики"
        ordering = [
            "table_number",
        ]

    def __str__(self):
        return f"Столик №{self.table_number}"


class Reservation(models.Model):
    """Модель брони"""

    guests_name = models.CharField(max_length=50, verbose_name="ФИО", help_text="Укажите ФИО")
    table = models.ForeignKey(
        Table,
        on_delete=models.SET_NULL,
        verbose_name="Столик",
        help_text="Введите название категории",
        null=True,
        related_name="tables",
    )
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=11, verbose_name="Телефон", help_text="Укажите номер телефона")
    booking_date = models.DateTimeField(
        verbose_name="Дата и время бронирования",
        help_text="Укажите когда вы хотите забронировать столик (день и время)",
    )
    number_of_guests = models.IntegerField(verbose_name="Количество гостей", help_text="Укажите количество гостей")

    booking_end = models.DateTimeField(
        verbose_name="Дата и время окончания бронирования",
        help_text="Автоматически рассчитывается как начало бронирования + 4 часа",
        editable=False,  # Что бы не выводить в форму создания и изменения бронирования (автозаполнение)
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        """Автоматический рассчет окончания бронирования"""
        if self.booking_date:
            self.booking_end = self.booking_date + timedelta(hours=4)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Бронь"
        verbose_name_plural = "Брони"
        ordering = ["table", "phone", "booking_date", "guests_name"]

    def __str__(self):
        return self.guests_name


class Foto(models.Model):
    """Модель фото"""

    data_at = models.CharField(
        max_length=20, verbose_name="Дата создания фото", help_text="Добавьте дату создания фото"
    )

    # путь для сохранения фото столика
    image = models.ImageField(
        upload_to="data/image_foto",
        blank=True,
        null=True,
        verbose_name="Фото ",
        help_text="Загрузите фото",
    )

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фото"

    def __str__(self):
        return self.data_at


class Review(models.Model):
    """Модель отзыва"""

    name = models.CharField(max_length=20, verbose_name="Автор", help_text="Укажите свое имя", null=False, blank=False)
    review = models.CharField(max_length=200, verbose_name="Отзыв", help_text="Добавьте отзыв", blank=True, null=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return self.name
