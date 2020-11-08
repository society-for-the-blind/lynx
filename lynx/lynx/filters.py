import django_filters

from .models import Contact, ContactInfoView


class ContactFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('last_name', 'last_name'),
            ('first_name', 'first_name'),
        )

    )

    class Meta:
        model = ContactInfoView
        fields = {'last_name': ['icontains'],
                  'first_name': ['icontains'],
                  'intake_date': ['gt', 'lt'],
                  'age_group': ['exact'],
                  'email': ['icontains'],
                  'zip_code': ['icontains'],
                  'county': ['icontains'],
                  'phone': ['icontains'],
                  }
