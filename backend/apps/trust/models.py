from django.db import models
from apps.reviews.models import Review
from apps.products.models import Product


class ReviewScore(models.Model):
    """Résultat du scoring Isolation Forest pour une review précise."""
    review = models.OneToOneField(Review, on_delete=models.CASCADE, primary_key=True, related_name='score')

    near_dup_score = models.FloatField()
    is_burst_day = models.BooleanField()
    is_unverified = models.BooleanField()
    rating_deviation = models.FloatField()
    exclamation_count = models.FloatField()
    word_count = models.FloatField()
    avg_word_len = models.FloatField()
    positive_superlative_count = models.FloatField()
    negative_superlative_count = models.FloatField()

    iso_prediction = models.SmallIntegerField(help_text="-1 = anomalie suspecte, 1 = normale")
    iso_anomaly_score = models.FloatField(help_text="Plus bas = plus suspect")
    anomaly_frequency = models.FloatField(null=True, blank=True)

    computed_at = models.DateTimeField(auto_now=True)

    @property
    def is_trusted(self):
        return self.iso_prediction == 1

    def __str__(self):
        return f"Score({self.review_id})"


class ProductTrustReport(models.Model):
    """Rapport de confiance agrégé pour un produit : résumé + stats d'authenticité."""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True, related_name='trust_report')

    total_reviews = models.IntegerField()
    fake_count = models.IntegerField()
    authenticity_rate = models.FloatField(help_text="% de reviews jugées normales")
    raw_avg_rating = models.FloatField(help_text="Moyenne brute, toutes reviews confondues")
    adjusted_rating = models.FloatField(help_text="Moyenne calculée uniquement sur les reviews de confiance")

    summary_text = models.TextField(blank=True)
    pros = models.JSONField(default=list, blank=True)
    cons = models.JSONField(default=list, blank=True)
    verdict = models.TextField(blank=True)

    computed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"TrustReport({self.product_id})"
