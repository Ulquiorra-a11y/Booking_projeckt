from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'grade', 'created_at')
    list_filter = ('grade',)
    search_fields = ('description', 'booking__guest__email')