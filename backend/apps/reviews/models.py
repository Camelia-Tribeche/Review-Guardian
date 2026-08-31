from django.db import models
from apps.products.models import Product


class Review(models.Model):
    """Une review d'un produit. Ajoutée manuellement (admin ou import CSV) — pas de scraping."""
    review_id = models.CharField(max_length=30, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')

    rating = models.FloatField()
    review_title = models.CharField(max_length=255, blank=True)
    review_url = models.URLField(blank=True)
    review_position = models.IntegerField(null=True, blank=True)
    verified_purchase = models.BooleanField(default=False)
    helpful_vote_count = models.IntegerField(default=0)
    sentiment_score = models.FloatField(null=True, blank=True)

    content_clean = models.TextField()
    text_length = models.IntegerField(null=True, blank=True)

    posted_at = models.DateTimeField(null=True, blank=True, help_text="Date de la review sur Amazon")
    added_at = models.DateTimeField(auto_now_add=True, help_text="Date d'ajout dans notre DB")

    class Meta:
        ordering = ['-posted_at']
        indexes = [
            models.Index(fields=['product', 'posted_at']),
        ]

    def __str__(self):
        return f"{self.review_id} ({self.product_id})"
