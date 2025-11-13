from django import template

register = template.Library()

@register.filter
def has_program(programs, program_name):
    return programs.filter(program=program_name).exists()

@register.filter
def has_any_oib(programs):
    """Return True if any program in the queryset has is_oib == True."""
    return programs.filter(is_oib=True).exists()