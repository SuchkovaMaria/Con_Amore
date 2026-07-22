from django.contrib import admin

from con_amore.models import Table, Reservation, Foto, Review


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("id", "table_number", "description", "number_of_guests")
    list_editable = ("table_number",)


@admin.register(Foto)
class FotoAdmin(admin.ModelAdmin):
    list_display = ("id", "data_at",)
    list_filter = ("data_at",)
    search_fields = ("data_at",)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "guests_name", "table", "email", "phone", "booking_date", "booking_end", "number_of_guests")
    list_filter = ("guests_name",)
    search_fields = ("guests_name", "phone", "table")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "review")
    list_filter = ("name",)
    search_fields = ("name",)

