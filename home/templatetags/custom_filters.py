from django import template

register = template.Library()

@register.filter
def split_languages(value):
    if value:
        return [lang.strip() for lang in value.split(',')]
    return []
