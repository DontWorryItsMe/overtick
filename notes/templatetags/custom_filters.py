# C:\Users\Admin\overtick\notes\templatetags\custom_filters.py

from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(name='highlight')
def highlight(text, search):
    highlighted = re.sub(f'({search})', r'<mark>\1</mark>', text, flags=re.IGNORECASE)
    return mark_safe(highlighted)

@register.filter(name='instanceof')
def isinstanceof(obj, cls_name):
    return obj.__class__.__name__ == cls_name
