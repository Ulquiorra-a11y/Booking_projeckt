from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.listings.models import Listing, Photos
from apps.listings.serializers import ListingSerializer, ListingShortUpdateSerializer, PhotoSerializer
from core.permissions import IsOwnerOrReadOnly



class ListingViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Listing.objects.select_related('owner').prefetch_related('photos')

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update','list'):
            return ListingShortUpdateSerializer
        return ListingSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def search(self, request):
        check_in_str = request.query_params.get('check_in')
        check_out_str = request.query_params.get('check_out')

        queryset = self.get_queryset().filter(is_active=True)

        city = request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)

        min_guests = request.query_params.get('guests')
        if min_guests:
            queryset = queryset.filter(max_guests__gte=min_guests)

        if check_in_str and check_out_str:
            check_in = parse_date(check_in_str)
            check_out = parse_date(check_out_str)

            if not check_in or not check_out:
                return Response({'detail': 'Incorrect format for "check_in" and "check_out" parameters.'},
                    status=status.HTTP_400_BAD_REQUEST)

            available_ids = [
                listing.id for listing in queryset
                if listing.is_available_for(check_in, check_out)
            ]
            queryset = queryset.filter(id__in=available_ids)

        serializer = ListingShortUpdateSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK)

class PhotoViewSet(ModelViewSet):
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Photos.objects.select_related('listing')

        listing_id = self.request.query_params.get('listing')
        if listing_id:
            queryset = queryset.filter(listing_id=listing_id)

        return queryset

    def perform_create(self, serializer):
        listing = serializer.validated_data['listing']

        if listing.owner_id != self.request.user.id:
            raise PermissionDenied('You can anly add photos for your own listing.')

        serializer.save()

    def perform_update(self, serializer):
        if serializer.instance.listing.owner_id != self.request.user.id:
            raise PermissionDenied('You can only edit photos of your ads.')

        serializer.save()

    def perform_destroy(self, instance):
        if instance.listing.owner_id != self.request.user.id:
            raise PermissionDenied('You can only delete photos of your ads.')

        instance.delete()