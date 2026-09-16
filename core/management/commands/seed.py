import io
import random
from datetime import timedelta
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker
from PIL import Image, ImageDraw

from apps.users.models import Customer
from apps.listings.models import Listing, Photos
from apps.bookings.models import Booking, BookingStatus
from apps.reviews.models import Review

fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Наполняет базу данных тестовыми данными'

    def add_arguments(self, parser):
        parser.add_argument('--customers', type=int, default=20)
        parser.add_argument('--listings', type=int, default=30)
        parser.add_argument('--bookings', type=int, default=50)
        parser.add_argument('--clear', action='store_true')

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()

        with transaction.atomic():
            customers = self.create_customers(options['customers'])
            listings = self.create_listings(customers, options['listings'])
            self.create_photos(listings)
            bookings = self.create_bookings(options['bookings'], customers, listings)
            self.create_reviews(bookings)

        self.stdout.write(self.style.SUCCESS('База данных успешно наполнена тестовыми данными.'))

    def clear_data(self):
        self.stdout.write('Очищаю старые данные...')
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Photos.objects.all().delete()
        Listing.all_objects.all().delete()
        Customer.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING('Старые данные удалены.'))

    def create_customers(self, count):
        self.stdout.write(f'Создаю {count} пользователей...')
        customers = []

        for _ in range(count):
            customer = Customer.objects.create_user(
                email=fake.unique.email(),
                password='testpass123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=80),
                phone_number=fake.phone_number()[:20],
            )
            customers.append(customer)

        self.stdout.write(self.style.SUCCESS(f'  Создано {len(customers)} пользователей.'))
        return customers

    def create_listings(self, customers, count):
        self.stdout.write('Создаю объявления...')
        listings = []

        for _ in range(count):
            owner = random.choice(customers)
            listing = Listing(
                title=fake.sentence(nb_words=6).rstrip('.'),
                description=fake.text(max_nb_chars=400),
                country=fake.country(),
                city=fake.city(),
                street=fake.street_name(),
                house_number=str(fake.building_number()),
                is_active=random.choices([True, False], weights=[85, 15])[0],
                rooms=random.randint(1, 6),
                max_guests=random.randint(1, 10),
                owner=owner,
                price=Decimal(random.randrange(1500, 15000, 500)),
            )
            listing.save()
            listings.append(listing)

        self.stdout.write(self.style.SUCCESS(f'  Создано {len(listings)} объявлений.'))
        return listings

    def generate_fake_image(self, width=800, height=600):
        color = (
            random.randint(50, 220),
            random.randint(50, 220),
            random.randint(50, 220),
        )
        image = Image.new('RGB', (width, height), color=color)
        draw = ImageDraw.Draw(image)
        draw.text((20, 20), fake.word(), fill=(255, 255, 255))

        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)

        return ContentFile(buffer.read(), name=f'{fake.uuid4()}.jpg')

    def create_photos(self, listings):
        self.stdout.write('Создаю фото для объявлений...')
        total = 0

        for listing in listings:
            photo_count = random.randint(2, 6)
            for i in range(photo_count):
                photo = Photos(
                    listing=listing,
                    is_main=(i == 0),
                    order=i,
                )
                photo.image.save(
                    f'{fake.uuid4()}.jpg',
                    self.generate_fake_image(),
                    save=False,
                )
                photo.save()
                total += 1

        self.stdout.write(self.style.SUCCESS(f'  Создано {total} фото.'))

    def create_bookings(self, count, customers, listings):
        self.stdout.write('Создаю бронирования...')
        bookings_to_create = []
        existing_ranges = {}  # listing_id -> список (check_in, check_out) уже выбранных в этом запуске
        attempts = 0
        max_attempts = count * 5

        while len(bookings_to_create) < count and attempts < max_attempts:
            attempts += 1
            listing = random.choice(listings)
            guest = random.choice(customers)

            if guest.id == listing.owner_id:
                continue

            if random.random() < 0.5:
                check_in = timezone.now().date() - timedelta(days=random.randint(5, 300))
                status = BookingStatus.COMPLETED
            else:
                check_in = timezone.now().date() + timedelta(days=random.randint(1, 200))
                status = random.choice([BookingStatus.PENDING, BookingStatus.CONFIRMED])

            nights = random.randint(1, 14)
            check_out = check_in + timedelta(days=nights)

            # проверка пересечения с уже сохранёнными в базе бронями
            overlapping_db = Booking.objects.filter(
                listing=listing,
                status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.COMPLETED],
                check_in__lt=check_out,
                check_out__gt=check_in,
            ).exists()

            # проверка пересечения с бронями, которые ещё не сохранены (в этом же запуске)
            overlapping_pending = any(
                check_in < existing_out and check_out > existing_in
                for existing_in, existing_out in existing_ranges.get(listing.id, [])
            )

            if overlapping_db or overlapping_pending:
                continue

            bookings_to_create.append(Booking(
                guest=guest,
                listing=listing,
                check_in=check_in,
                check_out=check_out,
                guests_count=random.randint(1, listing.max_guests),
                status=status,
                total_price=listing.price * nights,
            ))
            existing_ranges.setdefault(listing.id, []).append((check_in, check_out))

        Booking.objects.bulk_create(bookings_to_create)

        self.stdout.write(self.style.SUCCESS(f'  Создано {len(bookings_to_create)} бронирований.'))
        return bookings_to_create

    def create_reviews(self, bookings):
        self.stdout.write('Создаю отзывы...')
        completed_bookings = [b for b in bookings if b.status == BookingStatus.COMPLETED]
        total = 0

        for booking in completed_bookings:
            if random.random() < 0.7:
                Review.objects.create(
                    booking=booking,
                    description=fake.paragraph(nb_sentences=3),
                    grade=random.randint(1, 5),
                )
                total += 1

        self.stdout.write(self.style.SUCCESS(f'  Создано {total} отзывов.'))