from django import template
import re

register = template.Library()

@register.filter(name='remove_img_tags')
def remove_img_tags(value):
    return re.sub(r'<img[^>]*>', '', value)
    # return value.lower()
