import django_filters

from .models import Contact


class ContactFilter(django_filters.FilterSet):
    # price = django_filters.NumberFilter()
    # price__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gt')
    # price__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lt')
    #
    # release_year = django_filters.NumberFilter(field_name='release_date', lookup_expr='year')
    # release_year__gt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__gt')
    # release_year__lt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__lt')

    last_name = django_filters.CharFilter(field_name='last_name', lookup_expr='icontains')
    first_name = django_filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    email__email = django_filters.CharFilter(lookup_expr='icontains')
    address__zip_code = django_filters.CharFilter(lookup_expr='icontains')
    address__county = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Contact
        # fields = {'last_name': ['icontains'],
        #           'first_name': ['icontains'],
        #           'intake__intake_date': ['gt', 'lt'],
        #           'intake__age_group': ['exact'],
        #           'email__email': ['icontains'],
        #           'address__zip_code': ['icontains'],
        #           'address__county': ['icontains'],
        #           }