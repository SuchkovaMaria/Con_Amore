from django import template

register = template.Library()


@register.filter()
def media_filter(filename):
    """Поиск фото по столикам"""
    if filename:
        return f"/media/{filename}"
    return "#"
