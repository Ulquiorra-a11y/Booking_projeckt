import django_filters

from apps.listings.models import Listing


class ListingFilter(django_filters.FilterSet):
    """
    FilterSet for Listing search, exposed via query params on the
    listings endpoint.

    Supports range filtering on price and room count (`*_min`/`*_max`)
    and a case-insensitive partial match on city. Does not cover
    date-based availability — that's handled separately by
    `Listing.is_available_for()` (see the `search` action), since it
    requires checking against the related Booking model rather than
    filtering fields on Listing itself.
    """
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    rooms_min = django_filters.NumberFilter(field_name='rooms', lookup_expr='gte')
    rooms_max = django_filters.NumberFilter(field_name='rooms', lookup_expr='lte')

    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')

    class Meta:
        model = Listing
        fields = ['price_min', 'price_max', 'rooms_min', 'rooms_max', 'city']