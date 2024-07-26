# C:\Users\Admin\overtick\notes\templatetags\instanceof.py

from django import template

register = template.Library()

@register.filter(name='instanceof')
def instanceof(obj, class_name):
    return obj.__class__.__name__.lower() == class_name.lower()