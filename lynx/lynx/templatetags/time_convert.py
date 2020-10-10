from django import template

register = template.Library()

SIP_UNITS = ((.25, "15 Minutes"), (.5, "30 Minutes"), (.75, "45 Minutes"), (1, "1 Hour"), (1.25, "1 Hour 15 Minutes"),
         (1.5, "1 Hour 30 Minutes"), (1.75, "1 Hour 45 Minutes"), (2, "2 Hours"), (2.25, "2 Hours 15 Minutes"),
         (2.5, "2 Hours 30 Minutes"), (2.75, "2 Hours 45 Minutes"), (3, "3 Hours"), (3.25, "3 Hours 15 Minutes"),
         (3.5, "3 Hours 30 Minutes"), (3.75, "3 Hours 45 Minutes"), (4, "4 Hours"), (4.25, "4 Hours 15 Minutes"),
         (4.5, "4 Hours 30 Minutes"), (4.75, "4 Hours 45 Minutes"), (5, "5 Hours"), (5.25, "5 Hours 15 Minutes"),
         (5.5, "5 Hours 30 Minutes"), (5.75, "5 Hours 45 Minutes"), (6, "6 Hours"), (6.25, "6 Hours 15 Minutes"),
         (6.5, "6 Hours 30 Minutes"), (6.75, "6 Hours 45 Minutes"), (7, "7 Hours"), (7.25, "7 Hours 15 Minutes"),
         (7.5, "7 Hours 30 Minutes"), (7.75, "7 Hours 45 Minutes"), (8, "8 Hours"))

@register.filter
def convert_fractions(value):
    if value:
        time_hours = SIP_UNITS[value]
        return time_hours
    else:
        return value
