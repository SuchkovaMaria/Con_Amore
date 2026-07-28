from django import template

register = template.Library()


@register.filter()
def media_filter(filename):
    """Поиск фото по столикам"""
    if filename:
        return f"/media/{filename}"
    return "#"


# Добавьте новые теги для работы с URL параметрами
@register.simple_tag
def sort_url(request, sort_field):
    """
    Генерация URL для сортировки с сохранением всех параметров.
    Использование: {% sort_url request 'table_number' %}
    Для поиска свободных столов по указанным параметрам
    """
    params = request.GET.copy()

    # Добавление/обновление параметра сортировки
    if sort_field:
        params["sort"] = sort_field
    else:
        params.pop("sort", None)

    return params.urlencode()


@register.simple_tag
def reset_sort_url(request):
    """
    Генерация URL для сброса сортировки.
    Использование: {% reset_sort_url request %}
    Убирает из URL параметр сортировки
    """
    params = request.GET.copy()

    # Удаление пустых параметров
    for key in list(params.keys()):
        if not params[key]:
            del params[key]

    # Удаление параметров сортировки
    params.pop("sort", None)

    return params.urlencode()


# @register.simple_tag
# def url_with_params(request, **kwargs):
#     """
#     Добавление параметров к текущему URL, сохраняя существующие.
#     Использование: {% url_with_params request sort='table_number' date='2026-07-25' %}
#     Для добавления сортировки по номеру столика или количеству гостей
#     """
#     params = request.GET.copy()
#
#     # Удаление пустых параметров
#     for key in list(params.keys()):
#         if not params[key]:
#             del params[key]
#
#     # Обновление или добавление новых параметров
#     for key, value in kwargs.items():
#         if value is not None:
#             params[key] = value
#         else:
#             # Если значение None - удаление параметра
#             params.pop(key, None)
#
#     return params.urlencode()
#
#
# @register.simple_tag
# def keep_params(request, *keys):
#     """
#     Сохранение указанные параметры.
#     Использование: {% keep_params request 'date' 'time' 'guests' %}
#     Генерация URL для бронирования столика
#     """
#     params = request.GET.copy()
#
#     # Удаление всех параметров, кроме указанных
#     for key in list(params.keys()):
#         if key not in keys or not params[key]:
#             del params[key]
#
#     return params.urlencode()
