from django.utils.dateparse import parse_date
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from apps.listings.models import Listing, Photos
from apps.listings.serializers import ListingSerializer, ListingShortUpdateSerializer, PhotoSerializer
from core.filters import ListingFilter
from core.permissions import IsOwnerOrReadOnly


class ListingListViewSet(ReadOnlyModelViewSet):
    # serializer_class = ListingSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']
    filterset_class = ListingFilter

    def get_queryset(self):
        return Listing.objects.filter(is_active=True).select_related('owner').prefetch_related('photos')

    def get_serializer_class(self):
        if self.action == 'list':
            return ListingShortUpdateSerializer
        return ListingSerializer

class ListingViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ListingFilter

    def get_queryset(self):
        return Listing.objects.filter(owner=self.request.user).select_related('owner').prefetch_related('photos')

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update',):
            return ListingShortUpdateSerializer
        return ListingSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Filter active listings down to those available for a given date range.

        Meant to be combined with the standard `ListingFilter` query params
        (city, price, rooms, property_type) via the same `/listings/search/`
        endpoint — this action adds the one thing `ListingFilter` can't do:
        checking availability against existing bookings, which requires
        comparing against the `Booking` model rather than filtering fields
        on `Listing` itself.

        Query params:
            check_in (str): ISO date (YYYY-MM-DD). Required together with check_out.
            check_out (str): ISO date (YYYY-MM-DD). Required together with check_in.

        Returns:
            Response: 200 with the filtered listing list, or 400 if the dates
            are missing or malformed.
        """
        check_in_str = request.query_params.get('check_in')
        check_out_str = request.query_params.get('check_out')

        queryset = self.filter_queryset(self.get_queryset())

        if check_in_str and check_out_str:
            check_in = parse_date(check_in_str)
            check_out = parse_date(check_out_str)

            if not check_in or not check_out:
                return Response(
                    {'detail': 'Incorrect format for "check_in" and "check_out" parameters.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            available_ids = [
                listing.id for listing in queryset
                if listing.is_available_for(check_in, check_out)
            ]
            queryset = queryset.filter(id__in=available_ids)

        serializer = ListingShortUpdateSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PhotoViewSet(ModelViewSet):
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]

    def get_queryset(self):
        queryset = Photos.objects.select_related('listing')

        listing_id = self.request.query_params.get('listing')
        if listing_id:
            queryset = queryset.filter(listing_id=listing_id)

        return queryset
