from django import template
from django.utils import timezone

register = template.Library()

@register.simple_tag
def current_timestamp():
    """Returns the current timestamp as an integer."""
    return int(timezone.now().timestamp())
