import secrets

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect

from users.forms import UserRegisterForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.models import User
from config.settings import EMAIL_HOST_USER


class UsersCreateView(CreateView):
    """Класс добавления отзыва"""

    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")


    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(14)
        user.token = token
        password = form.cleaned_data.get('password1')
        user.set_password(password)
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}"
        send_mail(
            subject="Подтверждение регистрации в Con Amore",
            message=f"Приветствуем. Для вступления в нашу дружную команду Управляющих Con Amore, подтвердите регистрацию перейдя по ссылке {url} и ожидайте включения вас в группу",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


def email_verification(request, token):

    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse_lazy("users:login"))
