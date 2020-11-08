import django_filters

from .models import ContactInfoView

class ContactFilter(django_filters.FilterSet):

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
                  }
