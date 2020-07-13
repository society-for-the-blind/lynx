from django import template
import calendar

register = template.Library()

@register.filter
def month_name(value):
    if len(value) < 3:
        return calendar.month_name[value]
    else:
        return value
