from django import template
import calendar

register = template.Library()

@register.filter
def month_name(value):
    if len(value) < 3:
        value = int(value)
        return calendar.month_name[value]
    else:
        return value

@register.filter
def month_number(value):
    if len(value) > 3:
        MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7,
                  "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
        return MONTHS[value]
    else:
        return value
