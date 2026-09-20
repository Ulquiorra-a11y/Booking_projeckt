from django.contrib import admin
from .models import Listing, Photos

class PhotosInline(admin.TabularInline):
    model = Photos
    extra = 0

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'owner', 'price', 'is_active', 'created_at')
    list_filter = ('is_active', 'city', 'country')
    search_fields = ('title', 'city', 'owner__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PhotosInline]

@admin.register(Photos)
class PhotosAdmin(admin.ModelAdmin):
    list_display = ('listing', 'is_main', 'order', 'created_at')
    list_filter = ('is_main',)