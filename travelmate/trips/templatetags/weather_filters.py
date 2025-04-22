from django import template
import json

register = template.Library()

@register.filter
def json_decode(value):
    return json.loads(value)

@register.filter(name='split')
def split(value, delimiter):
    return value.split(delimiter)

@register.filter
def trim(value):
    return value.strip()