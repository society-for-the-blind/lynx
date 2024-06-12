import django_filters

from .models import IntakeNote, Sip1854Note, SipNote, Assignment, ContactInfoView, AGES, COUNTIES, PROGRAM
from django.contrib.auth.models import User
from django.db.models.functions import Lower
from django.db.models import Prefetch


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


from django import forms

class CustomDateTimeFilter(django_filters.Filter):
    field_class = forms.DateTimeField

class FullNameUserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.last_name}, {obj.first_name}"

class FullNameUserChoiceFilter(django_filters.ModelChoiceFilter):
    field_class = FullNameUserChoiceField

class AssignmentFilter(django_filters.FilterSet):
    program = django_filters.ChoiceFilter(choices=PROGRAM)
    instructors = User.objects.filter(groups__name='SIP').order_by(Lower('last_name'))
    instructor = FullNameUserChoiceFilter(queryset=instructors)
    assignment_date_gt = CustomDateTimeFilter(field_name='assignment_date', lookup_expr='gt', widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Assignments after date')
    assignment_date_lt = CustomDateTimeFilter(field_name='assignment_date', lookup_expr='lt', widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Assignments before date')

    class Meta:
        model = Assignment
        fields = [ 'assignment_date_gt', 'assignment_date_lt', 'program', 'instructor' ]

    def __init__(self, *args, **kwargs):
        super(AssignmentFilter, self).__init__(*args, **kwargs)
        if self.data == {}:
            self.queryset = self.queryset.none()
        else:
            # Prefetch the related SipNote objects through the Contact model
            sipnotes_prefetch = Prefetch('contact__sipnote_set', queryset=SipNote.objects.select_related('user').all(), to_attr='related_sipnotes')
            sip1854notes_prefetch = Prefetch('contact__sip1854note_set', queryset=Sip1854Note.objects.select_related('user').all(), to_attr='related_sip1854notes')
            intakenotes_prefetch = Prefetch('contact__intakenote_set', queryset=IntakeNote.objects.select_related('user').all(), to_attr='related_intakenotes')
            self.queryset = self.queryset.prefetch_related(sipnotes_prefetch, intakenotes_prefetch, sip1854notes_prefetch)
