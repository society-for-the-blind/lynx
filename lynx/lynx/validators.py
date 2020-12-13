from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_hours(value, authorization_id):
    from .views import units_to_hours
    from .models import LessonNote, Authorization
    note_list = LessonNote.objects.filter(authorization_id=authorization_id)
    authorization = Authorization.objects.get(id=authorization_id)

    total_units = 0
    for note in note_list:
        if note['billed_units']:
            units = float(note['billed_units'])
            total_units += units
    note_hours = units_to_hours(value)
    total_hours = units_to_hours(total_units) + note_hours
    if total_hours >= authorization['total_time']:
        hours_left = total_hours - note_hours
        raise ValidationError(
            _('Only %(hours_left) left on the authorization'),
            params={'hours_left': hours_left},
        )
