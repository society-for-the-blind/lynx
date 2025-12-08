import django_filters

from . import models  as lm
from django.contrib.auth.models import User
from django.db.models.functions import Lower
from datetime import date
from django import forms


# Normalize AGE_GROUP_BOUNDS into a list of (key,label,min_age,max_age)
def _load_age_groups():
    groups = []

    if not lm.AGE_GROUP_BOUNDS:
        return []

    # Support a few possible shapes for AGE_GROUP_BOUNDS:
    # - list of tuples (min, max, label)
    # - list of tuples (label, (min,max))
    # - dict-like { label: (min,max) }
    if isinstance(lm.AGE_GROUP_BOUNDS, dict):
        for label, bounds in lm.AGE_GROUP_BOUNDS.items():
            min_a, max_a = bounds
            min_val = -1 if min_a is None else int(min_a)
            max_val = -1 if max_a is None else int(max_a)
            groups.append((label, label, min_val, max_val))
    else:
        for i, item in enumerate(lm.AGE_GROUP_BOUNDS):
            if (isinstance(item, (list, tuple)) and len(item) == 3):
                # (min, max, label) - min/max may be None -> normalize to -1 for unbounded
                min_a, max_a, label = item
                min_val = -1 if min_a is None else int(min_a)
                max_val = -1 if max_a is None else int(max_a)
                groups.append((str(i), str(label), min_val, max_val))
            elif (isinstance(item, (list, tuple)) and len(item) == 2):
                # (label, (min,max))
                label, bounds = item
                min_a, max_a = bounds
                min_val = -1 if min_a is None else int(min_a)
                max_val = -1 if max_a is None else int(max_a)
                groups.append((str(i), str(label), min_val, max_val))
            else:
                # unknown shape -> skip
                continue
    return groups

_AGE_GROUPS = _load_age_groups()
AGE_GROUP_CHOICES = [('', 'Any')] + [(g[0], g[1]) for g in _AGE_GROUPS]

class ContactFilter(django_filters.FilterSet):
    intake_before = django_filters.DateFilter(
        field_name='intake__intake_date',
        lookup_expr='lt',
        widget=forms.SelectDateWidget(years=list(range(1900, 2100))),
        label='Intake before'
    )
    intake_after = django_filters.DateFilter(
        field_name='intake__intake_date',
        lookup_expr='gte',
        widget=forms.SelectDateWidget(years=list(range(1900, 2100))),
        label='Intake after'
    )
    age_group = django_filters.ChoiceFilter(
        choices=AGE_GROUP_CHOICES,
        method='filter_age_group',
        label='Age group'
    )
    email = django_filters.CharFilter(
        field_name='email__email',
        lookup_expr='icontains',
        label='Email contains'
    )
    county = django_filters.CharFilter(
        field_name='address__county',
        lookup_expr='icontains',
        label='County contains'
    )
    phone = django_filters.CharFilter(
        field_name='phone__phone',
        lookup_expr='icontains',
        label='Phone contains'
    )
    is_active = django_filters.BooleanFilter(
        field_name='active',
        label='Is client active'
    )
    program = django_filters.ModelChoiceFilter(
        field_name='programs',
        queryset=lm.Program.objects.order_by('program'),
        to_field_name='id',
        label='Program',
    )

    class Meta:
        model = lm.Contact
        fields = []

    def filter_age_group(self, queryset, name, value):
        """
        value is the key we stored in _AGE_GROUPS (first element) or '' for Any.
        We compute ages from the contact's latest intake birth_date (Contact.maybe_birth_date).
        For performance we iterate over queryset and build id__in list.
        """
        if not value:
            return queryset

        try:
            # find the bounds for the selected value
            sel = next(g for g in _AGE_GROUPS if g[0] == value)
        except StopIteration:
            return queryset

        _, _, min_age, max_age = sel

        # Prefetch intakes to reduce queries
        qs = queryset.prefetch_related('intake_set')
        matched_ids = []
        today = date.today()
        for contact in qs:
            dob = contact.maybe_birth_date()
            if not dob:
                continue
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if min_age != -1 and age < min_age:
                continue
            if max_age != -1 and age > max_age:
                continue
            matched_ids.append(contact.id)

        return queryset.filter(id__in=matched_ids)

class CustomDateTimeFilter(django_filters.Filter):
    field_class = forms.DateTimeField

class FullNameUserChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.empty_label = "All instructors"

    def label_from_instance(self, obj):
        return f"{obj.last_name}, {obj.first_name}"

class FullNameUserChoiceFilter(django_filters.ModelChoiceFilter):
    field_class = FullNameUserChoiceField

class AssignmentFilter(django_filters.FilterSet):
    program = django_filters.ModelChoiceFilter(
        field_name='program',
        queryset=lm.Program.objects.filter(is_oib=True).order_by('program'),
        empty_label='All programs'
    )
    instructors = User.objects.filter(groups__name='SIP').order_by(Lower('last_name'))
    instructor = FullNameUserChoiceFilter(queryset=instructors)
    assignment_date_gt = CustomDateTimeFilter(field_name='assignment_date', lookup_expr='gt', widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Assignments after date')
    assignment_date_lt = CustomDateTimeFilter(field_name='assignment_date', lookup_expr='lt', widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Assignments before date')

    class Meta:
        model = lm.Assignment
        fields = [ 'assignment_date_gt', 'assignment_date_lt', 'program', 'instructor' ]

    def __init__(self, *args, **kwargs):
        super(AssignmentFilter, self).__init__(*args, **kwargs)