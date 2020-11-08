import django_filters

from .models import Contact


class ContactFilter(django_filters.FilterSet):
    class Meta:
        model = Contact
        fields = {'last_name': ['icontains'],
                  'first_name': ['icontains'],
                  'intake__intake_date': ['gt', 'lt'],
                  'intake__age_group': ['exact'],
                  'email__email': ['icontains'],
                  'address_sip_code': ['icontains'],
                  'address__county': ['icontains'],

                  }