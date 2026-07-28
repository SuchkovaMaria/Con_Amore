from django.urls import reverse_lazy
from django.utils.timezone import localtime
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from datetime import datetime, timedelta
from con_amore.models import Table, Reservation, Foto, Review
from con_amore.forms import TableForm, ReservationForm, FotoForm, ReviewForm


class HomePageTemplateView(TemplateView):
    """Контролер для страницы Главная"""

    # Путь к шаблону для отображения
    template_name = "con_amore/home_page.html"

    def get_context_data(self, **kwargs):
        """Для добавление в контекст страницы данных по вариантам посадочных мест столиков"""
        context = super().get_context_data(**kwargs)

        # Уникальное количество мест из столиков
        context["unique_number_of_guests"] = list(
            Table.objects.values_list("number_of_guests", flat=True).distinct().order_by("number_of_guests")
        )

        return context


class TableListView(ListView):
    """Контролер для управления столиками (список столиков)"""

    model = Table
    # Путь к шаблону для отображения
    template_name = "con_amore/table_list.html"
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:home")

    def get_queryset(self):
        """Базовый queryset с сортировкой"""
        queryset = super().get_queryset()
        return self.apply_sorting(queryset)

    def apply_sorting(self, queryset):
        """Применяет сортировку к queryset"""
        sort_param = self.request.GET.get("sort")

        if sort_param:
            allowed_sorts = ["number_of_guests", "-number_of_guests", "table_number", "-table_number"]
            if sort_param in allowed_sorts:
                queryset = queryset.order_by(sort_param)

        return queryset

    def get_free_tables(self, tables, date, time, guests):
        """Возвращает свободные столики с учетом фильтров"""
        if not (date and time and guests):
            return tables

        try:
            # Фильтруем по количеству гостей
            tables = tables.filter(number_of_guests__gte=int(guests))

            # Преобразовываем дату и время
            booking_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            booking_end = booking_datetime + timedelta(hours=4)

            # Занятые столики
            reserved_table_ids = Reservation.objects.filter(
                booking_date__lt=booking_end, booking_end__gt=booking_datetime
            ).values_list("table_id", flat=True)

            # Свободные столики
            return tables.exclude(id__in=reserved_table_ids)

        except (ValueError, TypeError) as e:
            print(f"ERROR in get_free_tables: {e}")
            return tables

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получение параметров
        date = self.request.GET.get("date")
        time = self.request.GET.get("time")
        guests = self.request.GET.get("guests")

        # Базовый queryset с сортировкой
        tables = self.apply_sorting(Table.objects.all())

        # Получение свободных столиков
        free_tables = self.get_free_tables(tables, date, time, guests)

        # Добавление в контекст
        context["free_table"] = free_tables

        # Уникальное количество гостей (для фильтров)
        context["unique_number_of_guests"] = list(set(Table.objects.values_list("number_of_guests", flat=True)))

        # Выбранное количество гостей
        try:
            context["selected_guests"] = int(guests) if guests else None
        except ValueError:
            context["selected_guests"] = None

        return context


class TableCreateView(CreateView):
    """Класс добавления столика"""

    model = Table
    # Путь к шаблону для отображения
    template_name = "con_amore/table_form.html"
    # Какие поля будут в форме
    form_class = TableForm
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:table_list")


class TableDetailView(DetailView):
    """Контролер карточки столика"""

    model = Table


class TableUpdateView(UpdateView):
    """Класс редактирования столика"""

    model = Table
    # Путь к шаблону для отображения
    template_name = "con_amore/table_form.html"
    # Какие поля будут в форме
    form_class = TableForm
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:table_list")

    def get_success_url(self):
        """Функция перенаправления после сохранения изменений в карточке"""
        return reverse_lazy("con_amore:table_detail", args=(self.object.pk,))


class TableDeleteView(DeleteView):
    """Класс удаления столика"""

    model = Table
    # Путь к шаблону для отображения
    template_name = "con_amore/table_delete.html"
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:table_list")


class ReservationListView(ListView):
    """Контролер для управления бронями столиков"""

    model = Reservation
    # Путь к шаблону для отображения
    template_name = "con_amore/reservation_list.html"
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:reservation_list")

    def get_queryset(self):
        queryset = super().get_queryset()

        # Для фильтрации по имени гостя
        guests_name = self.request.GET.get("guests_name")
        if guests_name:
            queryset = queryset.filter(guests_name=guests_name)
        return queryset

    def get_context_data(self):
        """Добавляем данных в контекст шаблона"""
        context = super().get_context_data()
        object_list = Reservation.objects.all()
        # Варианты ФИО гостей
        context["unique_guests_name"] = list(set(reservation.guests_name for reservation in object_list))
        # Варианты посадочных мест у столов
        context["unique_number_of_guests"] = list(
            Table.objects.values_list("number_of_guests", flat=True).distinct().order_by("number_of_guests")
        )
        return context


class ReservationCreateView(CreateView):
    """Контролер добавления брони"""

    model = Reservation
    # Путь к шаблону для отображения
    template_name = "con_amore/reservation_form.html"
    # Какие поля будут в форме
    form_class = ReservationForm
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:home")

    def get_initial(self):
        """Подставление даты и времени из GET-параметров"""

        initial = super().get_initial()

        date = self.request.GET.get("date")
        time = self.request.GET.get("time")

        if date and time:
            try:
                dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
                initial["booking_date"] = dt.strftime("%Y-%m-%dT%H:%M")
                print(f"booking_date: {initial['booking_date']}")
            except ValueError as e:
                print(f"Ошибка преобразование даты: {e}")

        guests = self.request.GET.get("guests")
        if guests:
            try:
                initial["number_of_guests"] = int(guests)
                print(f"number_of_guests: {initial['number_of_guests']}")
            except ValueError as e:
                print(f"Ошибка преобразования гостей: {e}")

        print(f"initial: {initial}")
        return initial

    def get_context_data(self, **kwargs):
        """Добавление данных в контекст шаблона"""
        context = super().get_context_data(**kwargs)

        # Получение столика из URL
        table_id = self.kwargs.get("pk")
        if table_id:
            try:
                table = Table.objects.get(pk=table_id)
                context["table"] = table
            except Table.DoesNotExist:
                pass

        # Передача параметров из GET-запроса
        date = self.request.GET.get("date")
        time = self.request.GET.get("time")
        guests = self.request.GET.get("guests")

        context["booking_date"] = date
        context["booking_time"] = time
        context["booking_guests"] = guests

        # Формирование booking_datetime для скрытого поля
        date = self.request.GET.get("date", "")
        time = self.request.GET.get("time", "")

        if date and time:
            context["booking_datetime"] = f"{date} {time}"
        else:
            # Если нет параметров, используем заглушку
            context["booking_datetime"] = ""

        # # Принудительно устанавливаем, даже если пусто
        # context['booking_datetime'] = context.get('booking_datetime', '')

        return context

    def form_valid(self, form):
        """Привязка столика к бронированию"""

        print("=== form_valid ===")
        print(f"cleaned_data: {form.cleaned_data}")

        table_id = self.kwargs.get("pk")
        if table_id:
            try:
                table = Table.objects.get(pk=table_id)
                form.instance.table = table
                print(f"Привязан столик: {table.table_number}")
            except Table.DoesNotExist:
                print(f"Столик с ID {table_id} не найден")
                form.add_error(None, "Столик не найден")
                return self.form_invalid(form)

        response = super().form_valid(form)
        print(f"Создана бронь с ID: {self.object.pk}")
        return response

    def form_invalid(self, form):
        """Обработка ошибок формы"""

        print("=== form_invalid ===")
        print(f"Ошибки: {form.errors}")
        print(f"Данные: {form.data}")
        return super().form_invalid(form)


class ReservationDetailView(DetailView):
    """Контролер карточки брони"""

    model = Reservation


class ReservationUpdateView(UpdateView):
    """Контролер редактирования брони"""

    model = Reservation
    # Путь к шаблону для отображения
    template_name = "con_amore/reservation_update_form.html"
    # Какие поля будут в форме
    form_class = ReservationForm
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:reservation_list")

    def get_initial(self):
        """Предзаполнение датой и временем в форме редактирования"""
        initial = super().get_initial()
        if self.object and self.object.booking_date:
            # Преобразование в локальное время
            local_dt = localtime(self.object.booking_date)
            initial["booking_date"] = local_dt.strftime("%Y-%m-%dT%H:%M")
        return initial

    def get_success_url(self):
        """Функция перенаправления после сохранения изменений в карточке"""
        return reverse_lazy("con_amore:reservation_detail", args=(self.object.pk,))


class ReservationDeleteView(DeleteView):
    """Контролер удаления брони"""

    model = Reservation
    # Путь к шаблону для отображения
    template_name = "con_amore/reservation_delete.html"
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:reservation_list")


class FotoListView(ListView):
    """Контролер для списка фото"""

    model = Foto
    # Путь к шаблону для отображения
    template_name = "con_amore/foto_list.html"
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:foto_list")

    def get_context_data(self):
        """Добавление данных в контекст шаблона"""

        context = super().get_context_data()
        object_list = Review.objects.all()
        context["review_list"] = list(set(review for review in object_list))

        return context


class FotoCreateView(CreateView):
    """Контролер добавления фото"""

    model = Foto
    # Путь к шаблону для отображения
    template_name = "con_amore/foto_form.html"
    # Какие поля будут в форме
    form_class = FotoForm
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:foto_list")


class FotoDetailView(DetailView):
    """Контролер карточки фото"""

    model = Foto


class FotoUpdateView(UpdateView):
    """Контролер редактирования карточки фото"""

    model = Foto
    # Путь к шаблону для отображения
    template_name = "con_amore/foto_form.html"
    # Какие поля будут в форме
    form_class = FotoForm
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:foto_list")

    def get_success_url(self):
        """Функция перенаправления после сохранения изменений в карточке"""
        return reverse_lazy("con_amore:foto_detail", args=(self.object.pk,))


class FotoDeleteView(DeleteView):
    """Контролер удаления карточки фото"""

    model = Foto
    # Путь к шаблону для отображения
    template_name = "con_amore/foto_delete.html"
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:foto_list")


class ReviewListView(ListView):
    """Контролер для списка отзывов"""

    model = Review
    # Путь к шаблону для отображения
    template_name = "con_amore/foto_list.html"
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:foto_list")


class ReviewCreateView(CreateView):
    """Контролер добавления отзыва"""

    model = Review
    # Путь к шаблону для отображения
    template_name = "con_amore/review_form.html"
    # Какие поля будут в форме
    form_class = ReviewForm
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:foto_list")


class ReviewDetailView(DetailView):
    """Контролер карточки отзыва"""

    model = Review


class ReviewUpdateView(UpdateView):
    """Класс редактирования карточки отзыва"""

    model = Review
    # Путь к шаблону для отображения
    template_name = "con_amore/review_form.html"
    # Какие поля будут в форме
    form_class = ReviewForm
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:foto_list")

    def get_success_url(self):
        """Функция перенаправления после сохранения изменений в карточке"""
        return reverse_lazy("con_amore:foto_detail", args=(self.object.pk,))


class ReviewDeleteView(DeleteView):
    """Контролер удаления карточки отзыва"""

    model = Review
    # Путь к шаблону для отображения
    template_name = "con_amore/foto_delete.html"
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:foto_list")


class ContactsTemplateView(TemplateView):
    """Контролер для страницы Контакты"""

    # Путь к шаблону для отображения
    template_name = "con_amore/contacts.html"
