from django.contrib.auth.forms import UserCreationForm

from con_amore.forms import StyleFormMixin
from users.models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    """Класс формы регистрация пользователя"""

    class Meta:
        model = User
        fields = ["email", "password1", "password2"]
