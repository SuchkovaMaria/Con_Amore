from datetime import datetime, timedelta

from django.db.models import BooleanField
from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
from con_amore.models import Table, Reservation, Foto, Review


class StyleFormMixin:
    """Класс стилизации форм"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class TableForm(StyleFormMixin, ModelForm):
    """Класс формы создания/изменения столика"""

    class Meta:
        model = Table
        fields = ["table_number", "description", "image", "number_of_guests"]

class ReservationForm(StyleFormMixin, ModelForm):
    """Класс формы создания/изменения брони"""


    def clean_booking_date(self):
        """Валидация даты и времени бронирования"""
        booking_datetime = self.cleaned_data.get('booking_date')

        if not booking_datetime:
            return booking_datetime

        booking_time = booking_datetime.time()

        OPEN_TIME = "10:00"
        CLOSE_TIME = "23:00"

        open_time = datetime.strptime(OPEN_TIME, '%H:%M').time()
        close_time = datetime.strptime(CLOSE_TIME, '%H:%M').time()

        # 1. Проверка: время не раньше открытия
        if booking_time < open_time:
            raise ValidationError(
                f'Ресторан открывается в {OPEN_TIME}. Пожалуйста, выберите время позже.'
            )

        # 2. Проверка: время не позже закрытия
        if booking_time > close_time:
            raise ValidationError(
                f'Ресторан закрывается в {CLOSE_TIME}. Пожалуйста, выберите время раньше.'
            )

        # 3. Проверка: бронь на 4 часа должна заканчиваться до закрытия
        booking_end = booking_datetime + timedelta(hours=4)
        print(booking_end)
        print(close_time)
        if booking_end.date() > booking_datetime.date() or booking_end.time() > close_time:
            raise ValidationError(
                f'Бронирование на 4 часа. Время окончания ({booking_end.strftime("%H:%M")}) '
                f'позже закрытия ресторана ({CLOSE_TIME}). '
                f'Пожалуйста, выберите более раннее время.'
            )

        # 4. Проверка: дата не в прошлом
        if booking_datetime.date() < datetime.now().date():
            raise ValidationError('Нельзя бронировать столик на прошедшую дату.')

        # 5. Проверка: если сегодня, время не должно быть в прошлом
        if booking_datetime.date() == datetime.now().date():
            if booking_datetime.time() < datetime.now().time():
                raise ValidationError('Нельзя бронировать столик на прошедшее время.')

        return booking_datetime

    class Meta:
        model = Reservation
        fields = ['guests_name', 'email', 'phone', 'booking_date', 'number_of_guests']

        widgets = {
            'booking_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'number_of_guests': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Количество гостей'}
            ),
            'guests_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Иванов Иван Иванович'}
            ),
            'email': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'email@example.com'}
            ),
            'phone': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '79231234567 (только цифры)'}
            ),
        }


class FotoForm(StyleFormMixin, ModelForm):
    """Класс формы создания/изменения карточки фото"""

    class Meta:
        model = Foto
        fields = ["data_at", "image",]


class ReviewForm(StyleFormMixin, ModelForm):
    """Класс формы создания/изменения карточки отзыва"""

    class Meta:
        model = Review
        fields = ["name", "review"]