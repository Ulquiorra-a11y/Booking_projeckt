from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('listing', 'guest', 'check_in', 'check_out', 'status', 'total_price')
    list_filter = ('status',)
    search_fields = ('listing__title', 'guest__email')
    readonly_fields = ('total_price', 'created_at')