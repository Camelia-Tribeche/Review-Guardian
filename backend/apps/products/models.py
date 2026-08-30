from django.db import models


class Product(models.Model):
    """Un produit Amazon, identifié par son ASIN (unique sur Amazon)."""
    asin = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['asin']

    def __str__(self):
        return self.name or self.asin
