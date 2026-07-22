from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.timezone import localtime
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from datetime import datetime, timedelta
from con_amore.models import Table, Reservation, Foto, Review
from con_amore.forms import TableForm, ReservationForm, FotoForm, ReviewForm


class HomePageTemplateView(TemplateView):
    """Контролер для страницы Главная"""

    template_name = "con_amore/home_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Уникальное количество мест из столиков
        context['unique_number_of_guests'] = list(
            Table.objects.values_list('number_of_guests', flat=True)
            .distinct().order_by('number_of_guests')
        )

        return context


class TableListView(ListView):
    """Контролер для управления столиками (список столиков)"""

    model = Table
    template_name = "con_amore/table_list.html"
    success_url = reverse_lazy("con_amore:home")

    def get_queryset(self):
        """Обработка сортировки"""
        queryset = super().get_queryset()
        sort_param = self.request.GET.get('sort')

        if sort_param:
            allowed_sorts = ['number_of_guests', '-number_of_guests', 'table_number', '-table_number']
            if sort_param in allowed_sorts:
                queryset = queryset.order_by(sort_param)

        return queryset

    def get_context_data(self, **kwargs):  # ← Добавьте **kwargs
        context = super().get_context_data(**kwargs)

        # Уникальное количество гостей
        object_list = Table.objects.all()
        context['unique_number_of_guests'] = list(set(table.number_of_guests for table in object_list))
        print(object_list)

        # Получаем параметры из GET-запроса
        date = self.request.GET.get('date')
        time = self.request.GET.get('time')
        guests = self.request.GET.get('guests')
        print(f"DEBUG: date={date}, time={time}, guests={guests}")

        # Базовый queryset всех столиков
        tables = Table.objects.all()

        if date and time and guests:
            try:
                # 1. Фильтруем столики по количеству гостей
                tables = tables.filter(number_of_guests__gte=int(guests))

                # 2. Объединяем дату и время в один datetime
                booking_datetime = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M')

                # 3. Рассчитываем время окончания бронирования (+4 часа)
                booking_end = booking_datetime + timedelta(hours=4)

                # 4. Находим занятые столики на указанную дату и время
                #    (бронирования, которые пересекаются с выбранным временем)
                reserved_table_ids = Reservation.objects.filter(
                    booking_date__lt=booking_end,  # Начало брони раньше окончания выбранного времени
                    booking_end__gt=booking_datetime  # Конец брони позже начала выбранного времени
                ).values_list('table_id', flat=True)

                # 5. Исключаем занятые столики
                free_tables = tables.exclude(id__in=reserved_table_ids)
                print(f"DEBUG: free_tables={free_tables}")

                # 6. Добавляем в контекст
                context['free_table'] = free_tables
                print(f"DEBUG: date={date}, time={time}, guests={guests}")
                print(f"DEBUG: reserved_table_ids = {list(reserved_table_ids)}")
                print(f"DEBUG: free_tables = {list(free_tables.values_list('id', flat=True))}")

            except (ValueError, TypeError) as e:
                # Если ошибка при парсинге - показываем все столики
                context['free_table'] = Table.objects.all()
                print(f"ERROR: {e}")


        else:
            # Если параметры не указаны - показываем все столики
            context['free_table'] = Table.objects.all()
            context['free_table_count'] = Table.objects.count()

        # 7. Добавляем selected_guests для шаблона
        guests = self.request.GET.get('guests')
        if guests:
            try:
                context['selected_guests'] = int(guests)
            except ValueError:
                context['selected_guests'] = None
        else:
            context['selected_guests'] = None

        return context


class TableCreateView(CreateView):
    """Класс добавления столика"""

    model = Table
    # Название формы
    template_name = "con_amore/table_form.html"
    # Какие поля будут в форме создания
    form_class = TableForm
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:table_list")


class TableDetailView(DetailView):
    """Контролер карточки столика"""

    model = Table


class TableUpdateView(UpdateView):
    """Класс редактирования столика"""

    model = Table
    template_name = "con_amore/table_form.html"
    form_class = TableForm
    success_url = reverse_lazy("con_amore:table_list")

    def get_success_url(self):
        return reverse_lazy("con_amore:table_detail", args=(self.object.pk,))


class TableDeleteView(DeleteView):
    """Класс удаления столика"""

    model = Table
    template_name = "con_amore/table_delete.html"
    success_url = reverse_lazy("con_amore:table_list")


class ReservationListView(ListView):
    """Контролер для управления бронями столиков"""

    model = Reservation
    template_name = "con_amore/reservation_list.html"
    success_url = reverse_lazy("con_amore:reservation_list")

    def get_queryset(self):
        queryset = super().get_queryset()

        # Фильтрация по имени гостя
        guests_name = self.request.GET.get('guests_name')
        if guests_name:
            queryset = queryset.filter(guests_name=guests_name)
        return queryset

    def get_context_data(self):
        # Добавляем свои собственные данные в контекст шаблона
        context = super().get_context_data()
        object_list = Reservation.objects.all()
        context['unique_guests_name'] = list(set(reservation.guests_name for reservation in object_list))
        context['unique_number_of_guests'] = list(
            Table.objects.values_list('number_of_guests', flat=True).distinct().order_by('number_of_guests'))
        return context


class ReservationCreateView(CreateView):
    """Класс добавления брони"""

    model = Reservation
    # Название формы
    template_name = "con_amore/reservation_form.html"
    # Какие поля будут в форме создания
    form_class = ReservationForm
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:home")

    def get_initial(self):
        """Подставляем дату и время из GET-параметров"""
        initial = super().get_initial()

        date = self.request.GET.get('date')
        time = self.request.GET.get('time')

        if date and time:
            try:
                # Объединяем дату и время
                dt = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M')
                # Формат для datetime-local: YYYY-MM-DDTHH:MM
                initial['booking_date'] = dt.strftime('%Y-%m-%dT%H:%M')
            except ValueError:
                pass

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table_pk = self.kwargs.get('pk')
        if table_pk:
            context['table'] = get_object_or_404(Table, pk=table_pk)
        return context

    def form_valid(self, form):
        table_pk = self.kwargs.get('pk')
        if table_pk:
            form.instance.table = get_object_or_404(Table, pk=table_pk)
        return super().form_valid(form)


class ReservationDetailView(DetailView):
    """Контролер карточки брони"""

    model = Reservation


class ReservationUpdateView(UpdateView):
    """Класс редактирования брони"""

    model = Reservation
    template_name = "con_amore/reservation_form.html"
    form_class = ReservationForm
    success_url = reverse_lazy("con_amore:reservation_list")

    def get_initial(self):
        initial = super().get_initial()
        if self.object and self.object.booking_date:
            # Преобразуем в локальное время
            local_dt = localtime(self.object.booking_date)
            initial['booking_date'] = local_dt.strftime('%Y-%m-%dT%H:%M')
        return initial

    def get_success_url(self):
        return reverse_lazy("con_amore:reservation_detail", args=(self.object.pk,))


class ReservationDeleteView(DeleteView):
    """Класс удаления брони"""

    model = Reservation
    template_name = "con_amore/reservation_delete.html"
    success_url = reverse_lazy("con_amore:reservation_list")


class FotoListView(ListView):
    """Контролер для списка фото"""

    model = Foto
    template_name = "con_amore/foto_list.html"
    success_url = reverse_lazy("con_amore:foto_list")

    def get_context_data(self):
        # Добавляем свои собственные данные в контекст шаблона
        context = super().get_context_data()
        object_list = Review.objects.all()
        context['review_list'] = list(set(review for review in object_list))

        return context


class FotoCreateView(CreateView):
    """Класс добавления фото"""

    model = Foto
    # Название формы
    template_name = "con_amore/foto_form.html"
    # Какие поля будут в форме создания
    form_class = FotoForm
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:foto_list")


class FotoDetailView(DetailView):
    """Контролер карточки фото"""

    model = Foto


class FotoUpdateView(UpdateView):
    """Класс редактирования карточки фото"""

    model = Foto
    template_name = "con_amore/foto_form.html"
    form_class = FotoForm
    success_url = reverse_lazy("con_amore:foto_list")

    def get_success_url(self):
        return reverse_lazy("con_amore:foto_detail", args=(self.object.pk,))


class FotoDeleteView(DeleteView):
    """Класс удаления карточки фото"""

    model = Foto
    template_name = "con_amore/foto_delete.html"
    success_url = reverse_lazy("con_amore:foto_list")


class ReviewListView(ListView):
    """Контролер для списка отзывов"""

    model = Review
    template_name = "con_amore/foto_list.html"
    success_url = reverse_lazy("con_amore:foto_list")


class ReviewCreateView(CreateView):
    """Класс добавления отзыва"""

    model = Review
    # Название формы
    template_name = "con_amore/review_form.html"
    # Какие поля будут в форме создания
    form_class = ReviewForm
    # Куда перенаправляется после того как будет выполнено
    success_url = reverse_lazy("con_amore:foto_list")


class ReviewDetailView(DetailView):
    """Контролер карточки отзыва"""

    model = Review


class ReviewUpdateView(UpdateView):
    """Класс редактирования карточки отзыва"""

    model = Review
    template_name = "con_amore/review_form.html"
    form_class = ReviewForm
    success_url = reverse_lazy("con_amore:foto_list")

    def get_success_url(self):
        return reverse_lazy("con_amore:foto_detail", args=(self.object.pk,))


class ReviewDeleteView(DeleteView):
    """Класс удаления карточки отзыва"""

    model = Review
    template_name = "con_amore/foto_delete.html"
    success_url = reverse_lazy("con_amore:foto_list")


class ContactsTemplateView(TemplateView):
    """Контролер для страницы Контакты"""

    template_name = "con_amore/contacts.html"