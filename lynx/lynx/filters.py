import django_filters

from .models import Sip1854Assignment, Assignment, ContactInfoView, AGES, COUNTIES, STATUSES
from django.contrib.auth.models import User
from django.db.models.functions import Lower


class ContactFilter(django_filters.FilterSet):
    age_group = django_filters.ChoiceFilter(choices=AGES)
    county = django_filters.ChoiceFilter(choices=COUNTIES)
    active = django_filters.BooleanFilter(field_name='active')
    sip_client = django_filters.BooleanFilter(field_name='sip_client')
    core_client = django_filters.BooleanFilter(field_name='core_client')
    sip1854_client = django_filters.BooleanFilter(field_name='sip1854_client')

    class Meta:
        model = ContactInfoView
        fields = {'last_name': ['icontains'],
                  'first_name': ['icontains'],
                  'intake_date': ['gt', 'lt', 'exact'],
                  'age_group': ['exact'],
                  'email': ['icontains'],
                  'zip_code': ['icontains'],
                  'county': ['icontains'],
                  'phone': ['icontains'],
                  'active': ['exact'],
                  'sip_client': ['exact'],
                  'core_client': ['exact'],
                  'sip1854_client': ['exact'],
                  }

    def __init__(self, *args, **kwargs):
        super(ContactFilter, self).__init__(*args, **kwargs)
        if self.data == {}:
            self.queryset = self.queryset.none()


class AssignmentFilter(django_filters.FilterSet):
    assignment_status = django_filters.ChoiceFilter(choices=STATUSES)
    instructors = User.objects.filter(groups__name='SIP').order_by(Lower('last_name'))
    instructor = django_filters.ModelChoiceFilter(queryset=instructors)

    class Meta:
        model = Assignment
        fields = {
            'assignment_date': ['gt', 'lt'],
            'assignment_status': ['exact'],
            'instructor': ['exact']
        }

    def __init__(self, *args, **kwargs):
        super(AssignmentFilter, self).__init__(*args, **kwargs)
        if self.data == {}:
            self.queryset = self.queryset.none()
