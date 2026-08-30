from django.contrib import admin
from .models import ReviewScore, ProductTrustReport


@admin.register(ReviewScore)
class ReviewScoreAdmin(admin.ModelAdmin):
    list_display = ['review_id', 'iso_prediction', 'iso_anomaly_score', 'is_trusted']
    list_filter = ['iso_prediction']


@admin.register(ProductTrustReport)
class ProductTrustReportAdmin(admin.ModelAdmin):
    list_display = ['product', 'total_reviews', 'fake_count', 'authenticity_rate',
                     'raw_avg_rating', 'adjusted_rating', 'computed_at']
