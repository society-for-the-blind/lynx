import django_filters

from .models import ContactInfoView, AGES, COUNTIES


class ContactFilter(django_filters.FilterSet):
    age_group = django_filters.ChoiceFilter(choices=AGES)
    county = django_filters.ChoiceFilter(choices=COUNTIES)
    # active = django_filters.BooleanFilter(field_name='active')
    # sip_client = django_filters.BooleanFilter(field_name='sip_client')
    # core_client = django_filters.BooleanFilter(field_name='core_client')

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
                  # 'active': ['exact'],
                  # 'sip_client': ['exact'],
                  # 'core_client': ['exact'],
                  }

    def __init__(self, *args, **kwargs):
        super(ContactFilter, self).__init__(*args, **kwargs)
        if self.data == {}:
            self.queryset = self.queryset.none()
