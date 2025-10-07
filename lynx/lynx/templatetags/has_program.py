from django import template

register = template.Library()

@register.filter
def has_program(programs, program_name):
    return programs.filter(program=program_name).exists()