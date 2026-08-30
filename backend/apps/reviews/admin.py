from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['review_id', 'product', 'rating', 'verified_purchase', 'posted_at']
    list_filter = ['verified_purchase', 'rating']
    search_fields = ['review_id', 'product__asin', 'content_clean']
    autocomplete_fields = ['product']
