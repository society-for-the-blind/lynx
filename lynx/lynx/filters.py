import django_filters

from . import models  as lm
from django.contrib.auth.models import User
from django.db.models.functions import Lower
from django.db.models import Prefetch
from django import forms


class ContactFilter(django_filters.FilterSet):
    age_group = django_filters.ChoiceFilter(choices=lm.AGES)
    county = django_filters.ChoiceFilter(choices=lm.COUNTIES)
    active = django_filters.BooleanFilter(field_name='active')
    programs = django_filters.CharFilter(field_name='programs', lookup_expr='icontains', label='Programs')

    class Meta:
        model = lm.ContactInfoView
        fields = {
            'last_name': ['icontains'],
            'first_name': ['icontains'],
            'intake_date': ['gt', 'lt', 'exact'],
            'age_group': ['exact'],
            'email': ['icontains'],
            'zip_code': ['icontains'],
            'county': ['icontains'],
            'phone': ['icontains'],
            'active': ['exact'],
            'programs': ['icontains'],
        }

    def __init__(self, *args, **kwargs):
        super(ContactFilter, self).__init__(*args, **kwargs)
        if self.data == {}:
            self.queryset = self.queryset.none()


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