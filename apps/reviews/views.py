from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly

from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer
from core.permissions import IsReviewCreatorOrReadOnly


class ReviewViewSet(viewsets.ModelViewSet):

    serializer_class = ReviewSerializer
    permission_classes = [IsReviewCreatorOrReadOnly,IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.select_related('booking__guest','booking__listing')
        listing_id = self.request.query_params.get('listing')
        if listing_id:
            queryset = queryset.filter(booking__listing_id=listing_id)
            return queryset

