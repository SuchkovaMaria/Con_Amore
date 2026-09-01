from django.core.cache import cache

from con_amore.models import Table, Reservation
from config.settings import CACHE_ENABLED


def get_table_from_cache():
    """Получение списка столиков из кеша/БД"""

    if not CACHE_ENABLED:
        return Table.objects.all()
    key = "table_list"
    tables = cache.get(key)
    if tables is not None:
        return tables
    tables = Table.objects.all()
    cache.set(key, tables)
    return tables


def get_reservation_from_cache():
    """Получение списка броней из кеша/БД"""

    if not CACHE_ENABLED:
        return Reservation.objects.all()
    key = "reservation_list"
    reserves = cache.get(key)
    if reserves is not None:
        return reserves
    reserves = Reservation.objects.all()
    cache.set(key, reserves)
    return reserves
