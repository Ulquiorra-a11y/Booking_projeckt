# Booking Platform API

A Django REST Framework backend for an Airbnb/Booking.com-style property rental platform. Users can list properties, search and filter available listings, book stays for specific date ranges, and leave reviews after a completed stay.

This is a personal learning project built to practice Django, Django REST Framework, and containerized deployment.

## Features

- **Custom email-based authentication** — no usernames; login is via email + password
- **JWT authentication** (`djangorestframework-simplejwt`) for the API, alongside session/basic auth for browsable API testing
- **Listings** with up to 6 photos each, soft delete, and owner-only edit permissions
- **Search and filtering** on listings — keyword search (title/description), price range, room count range, city, sorting by price or creation date, plus a dedicated `search` endpoint that also filters by date availability
- **Booking system** with:
  - Race-condition-safe booking creation using `select_for_update()` inside an atomic transaction, so two guests can't double-book the same dates
  - Model-level validation preventing bookings in the past, checkout-before-checkin, and overlapping date ranges
  - A `Booking` service layer (`apps/bookings/services.py`) that also blocks a listing owner from booking their own listing and sends a confirmation email on success
- **Reviews** tied one-to-one to a completed booking, so a stay can only be reviewed once, by the guest who actually booked it
- **Soft delete** pattern on `Customer` and `Listing` (records are deactivated and timestamped instead of removed, keeping related `PROTECT`-ed rows intact)
- **UUID primary keys** on all models
- **Database indexes** on the fields used for filtering/sorting/lookups (price, city, status, dates, etc.)
- **Seed command** (`manage.py seed`) that populates the database with realistic fake data — including real Pillow-generated JPEG images for listing photos — via Faker
- **Auto-generated API docs** via `drf-spectacular` (OpenAPI schema, Swagger UI, Redoc)
- **Dockerized** — Django/Gunicorn + MySQL 8.4, ready for deployment (e.g. AWS EC2)

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| Framework | Django 6.1.1 |
| API | Django REST Framework 3.18 |
| Auth | `djangorestframework-simplejwt` |
| Filtering | `django-filter` |
| API Schema | `drf-spectacular` |
| Database | MySQL 8.4 (Docker/production), SQLite (local dev fallback) |
| Test data | Faker, Pillow |
| Deployment | Docker, Docker Compose, Gunicorn |

## Project Structure

```
config/                     # Django project settings, URLs, WSGI/ASGI entry points
core/                        # Shared base models, validators, permissions, filters, exceptions
  ├── models.py                  # UniqueID / TimeStampedModel abstract bases + shared enums
  │                               #   (Grades, Country, City, Guests, BookingStatus)
  ├── validators.py              # Date-related and phone-number validators
  ├── permissions.py             # Ownership-based DRF permissions
  ├── filters.py                 # ListingFilter (price/rooms/city query filtering)
  ├── exceptions.py              # Global exception handler (Django -> DRF errors)
  └── management/commands/seed.py   # Fake data seeder
apps/
  ├── users/                   # Custom Customer model, manager, registration/auth views
  ├── listings/                 # Listing & Photos models, views, serializers
  ├── bookings/                  # Booking model, booking service (overlap-safe creation), views
  └── reviews/                   # Review model, serializers, views
Dockerfile
docker-compose.yml
env.example
```

## Data Model Overview

- **Customer** — custom user model (`AUTH_USER_MODEL`), authenticated by email; a single user can act as both host and guest, soft-deletable
- **Listing** — a property owned by a `Customer`, with price per night, address, room/guest capacity, and a computed `average_rating`; `objects` returns only non-deleted listings, `all_objects` returns everything
- **Photos** — up to 6 images per listing (`MAX_PHOTOS`), with one photo optionally marked as `is_main` (automatically unmarking any previous main photo)
- **Booking** — links a `Customer` (guest) to a `Listing` for a `check_in`/`check_out` range; enforces no self-booking, no overlapping dates, and no bookings in the past, both at the model level and via a locking transaction in the service layer
- **Review** — one-to-one with a completed `Booking`; `user` and `listing` are read-only properties derived from the booking rather than separate foreign keys

## Getting Started

### Local development (SQLite)

```bash
git clone https://github.com/Ulquiorra-a11y/Booking_projeckt.git
cd Booking_projeckt
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp env.example .env       # fill in SECRET_KEY, DEBUG, ALLOWED_HOSTS, etc.
python manage.py migrate
python manage.py seed     # optional: populate with fake data
python manage.py runserver
```

By default `MYSQL=False` (or unset) makes the app use SQLite — no extra setup needed for local development.

### With Docker (MySQL)

```bash
docker-compose up --build
```

This starts two services:
- **`web`** — Django app served by Gunicorn (port `8000`), running `migrate` and `collectstatic` automatically on startup
- **`db`** — MySQL 8.4 (Django 6.1 requires MySQL 8.4 or later)

Make sure your `.env` has `MYSQL=True` and `DB_HOST=db` (the Compose service name) before running.

### Environment variables

See `env.example` for the full list:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True`/`False` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts |
| `MYSQL` | `True` to use MySQL, `False`/unset to fall back to SQLite |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | MySQL connection settings |
| `DB_ROOT_PASSWORD` | MySQL root password (Docker only) |

## API Overview

All endpoints are registered under the API root via DRF's `DefaultRouter`:

| Endpoint | Description |
|---|---|
| `POST /register/` | Register a new customer |
| `POST /login/`, `POST /login/refresh/` | Obtain/refresh a JWT pair |
| `GET/PATCH /profile/` | View or update the authenticated customer's profile |
| `POST /logout/` | Blacklist the current refresh token |
| `GET /listings/` | Public, read-only list of active listings (search, filter, sort) |
| `GET /listings/search/` | Active listings filtered by check-in/check-out availability |
| `GET/POST/PATCH/DELETE /listings/create/` | Owner-only CRUD on the authenticated user's own listings |
| `GET/POST/PATCH/DELETE /photos/` | Manage photos for a listing |
| `GET/POST/PATCH/DELETE /bookings/` | Create/view bookings (visible to the guest and the listing owner) |
| `GET/POST/PATCH/DELETE /reviews/` | Leave/view reviews for completed bookings |
| `/swagger/`, `/docs/`, `/api/schema/` | OpenAPI schema, Swagger UI, and Redoc (schema view is admin-only) |

## Seeding Test Data

```bash
python manage.py seed --clear
```

Optional flags: `--customers`, `--listings`, `--bookings` (defaults: 20 / 30 / 50). Generates fake customers, listings with real generated photos, a mix of past (completed) and upcoming bookings, and reviews for ~70% of completed stays — all overlap- and self-booking-safe.

## Notes

This is a learning project and is not production-hardened yet. Known areas for future work:
- Automated test suite (booking overlap, permissions, validators — test files exist but are currently mostly empty)
- Production deployment (AWS EC2, HTTPS/reverse proxy, `DEBUG=False` hardening)
- Rate limiting and additional API security measures

## License

Personal/educational project — no license specified.
