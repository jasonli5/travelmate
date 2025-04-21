from django import template
from django.forms import BoundField

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    if isinstance(value, BoundField):
        return value.as_widget(attrs={'class': css_class})
    return value  # fallback: just return the value as-is