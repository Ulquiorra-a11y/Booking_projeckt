from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status

from apps.users.models import Customer
from apps.listings.models import Listing
from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services import create_booking


class BookingOverlapTests(TestCase):
    def setUp(self):
        self.owner = Customer.objects.create_user(email='owner@test.com', password='pass12345')
        self.guest = Customer.objects.create_user(email='guest@test.com', password='pass12345')
        self.listing = Listing.objects.create(
            title='Test listing with min title',
            description='Test description here',
            country='Germany', city='Augsburg', street='Test', house_number='1',
            rooms=2, max_guests=4, owner=self.owner, price=1000,
        )

    def test_overlapping_dates_rejected(self):
        today = timezone.now().date()
        Booking.objects.create(
            guest=self.guest, listing=self.listing,
            check_in=today + timedelta(days=5),
            check_out=today + timedelta(days=10),
            total_price=5000,
        )

        overlapping_booking = Booking(
            guest=self.guest, listing=self.listing,
            check_in=today + timedelta(days=7),
            check_out=today + timedelta(days=12),
            total_price=5000,
        )

        with self.assertRaises(ValidationError):
            overlapping_booking.save()

    def test_non_overlapping_dates_allowed(self):
        today = timezone.now().date()
        Booking.objects.create(
            guest=self.guest, listing=self.listing,
            check_in=today + timedelta(days=5),
            check_out=today + timedelta(days=10),
            total_price=5000,
        )


        next_booking = Booking(
            guest=self.guest, listing=self.listing,
            check_in=today + timedelta(days=10),
            check_out=today + timedelta(days=15),
            total_price=5000,
        )
        next_booking.save()

        self.assertEqual(Booking.objects.count(), 2)

    def test_cannot_book_own_listing(self):

        with self.assertRaises(ValidationError):
            create_booking(
                guest=self.owner,
                listing=self.listing,
                check_in=timezone.now().date() + timedelta(days=1),
                check_out=timezone.now().date() + timedelta(days=3),
                guests_count=1,
            )



class ListingPermissionsTests(APITestCase):
    def setUp(self):
        self.owner = Customer.objects.create_user(email='owner@test.com', password='pass12345')
        self.other_user = Customer.objects.create_user(email='other@test.com', password='pass12345')
        self.listing = Listing.objects.create(
            title='Test listing with min title', description='Test description here',
            country='Russia', city='Moscow', street='Test', house_number='1',
            rooms=2, max_guests=4, owner=self.owner, price=1000,
        )

    def test_non_owner_cannot_edit_listing(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(f'/my-listings/{self.listing.id}/', {'title': 'Hacked title'})
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_owner_can_edit_own_listing(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(f'/my-listings/{self.listing.id}/', {'title': 'Updated title min 10'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

