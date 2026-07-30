from django import template

register = template.Library()


@register.filter()
def media_filter(filename):
    """Поиск фото по столикам"""
    if filename:
        return f"/media/{filename}"
    return "#"


# Добавление новых тегов для работы с URL параметрами
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

