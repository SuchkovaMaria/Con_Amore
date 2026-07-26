from datetime import timedelta
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from con_amore.models import Reservation
from config.settings import EMAIL_HOST_USER


@shared_task
def mail_about_reservation_execution():
    """Функция отправки напоминания о бронировании клиенту за 12 часов"""
    today = timezone.now()
    target_time = today + timedelta(hours=12)
    time_delta = timedelta(seconds=59) # временной запас что бы избежать пропуска резерва из-за задержек
    reserves = Reservation.objects.filter(
        booking_date__range=(target_time - time_delta, target_time + time_delta)
    )

    for reservation in reserves:
        local_time = timezone.localtime(reservation.booking_date) # Преобразование UTC-времени в локальный часовой пояс
        booking_date = local_time.strftime('%d.%m.%Y в %H:%M')  # Преобразование времени в подходящий формат для письма
        send_mail(
            subject="Напоминание от Con Amore",
            message=f"Приветствуем вас {reservation.guests_name}.\nХотим напомнить вам о брони столика в Con Amore {booking_date} (Номер вашего столика: {reservation.table.table_number})\nЖдем вас!\nВаш Con Amore.",
            from_email=EMAIL_HOST_USER,
            recipient_list=[reservation.email],
        )
