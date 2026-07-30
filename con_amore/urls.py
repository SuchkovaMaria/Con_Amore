from django.urls import path

from con_amore.apps import ConAmoreConfig
from django.views.decorators.cache import cache_page

from con_amore.views import (
    HomePageTemplateView,
    TableListView,
    TableCreateView,
    TableDetailView,
    TableUpdateView,
    TableDeleteView,
    ReservationListView,
    ReservationDetailView,
    ReservationCreateView,
    ReservationUpdateView,
    ReservationDeleteView,
    FotoListView,
    FotoDetailView,
    FotoCreateView,
    FotoUpdateView,
    FotoDeleteView,
    ReviewListView,
    ReviewDetailView,
    ReviewCreateView,
    ReviewUpdateView,
    ReviewDeleteView,
    ContactsTemplateView,
)

app_name = ConAmoreConfig.name


urlpatterns = [
    path("home/", HomePageTemplateView.as_view(), name="home"),
    path("con_amore/table_list/", cache_page(60)(TableListView.as_view()), name="table_list"),
    path("con_amore/<int:pk>/table/", TableDetailView.as_view(), name="table_detail"),
    path("con_amore/table_create/", TableCreateView.as_view(), name="table_create"),
    path("con_amore/<int:pk>/table_update/", TableUpdateView.as_view(), name="table_update"),
    path("con_amore/<int:pk>/table_delete/", TableDeleteView.as_view(), name="table_delete"),
    path("con_amore/reservation_list/", cache_page(60)(ReservationListView.as_view()), name="reservation_list"),
    path("con_amore/<int:pk>/reservation/", ReservationDetailView.as_view(), name="reservation_detail"),
    path("con_amore/<int:pk>/reservation_create/", ReservationCreateView.as_view(), name="reservation_create"),
    path("con_amore/<int:pk>/reservation_update/", ReservationUpdateView.as_view(), name="reservation_update"),
    path("con_amore/<int:pk>/reservation_delete/", ReservationDeleteView.as_view(), name="reservation_delete"),
    path("con_amore/foto_list/", FotoListView.as_view(), name="foto_list"),
    path("con_amore/<int:pk>/foto/", FotoDetailView.as_view(), name="foto_detail"),
    path("con_amore/foto_create/", FotoCreateView.as_view(), name="foto_create"),
    # path("con_amore/<int:pk>/foto_update/", FotoUpdateView.as_view(), name="foto_update"),
    # path("con_amore/<int:pk>/foto_delete/", FotoDeleteView.as_view(), name="foto_delete"),
    path("con_amore/review_list/", ReviewListView.as_view(), name="review_list"),
    # path("con_amore/<int:pk>/review/", ReviewDetailView.as_view(), name="review_detail"),
    path("con_amore/review_create/", ReviewCreateView.as_view(), name="review_create"),
    # path("con_amore/<int:pk>/review_update/", ReviewUpdateView.as_view(), name="review_update"),
    # path("con_amore/<int:pk>/review_delete/", ReviewDeleteView.as_view(), name="review_delete"),
    path("contacts/", ContactsTemplateView.as_view(), name="contacts"),
]
