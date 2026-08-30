from rest_framework import viewsets
from apps.products.models import Product
from apps.reviews.models import Review
from .serializers import ProductSerializer, ReviewSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/products/            -> liste des produits + leur rapport de confiance
    GET /api/products/{asin}/     -> détail d'un produit
    """
    queryset = Product.objects.select_related('trust_report').all()
    serializer_class = ProductSerializer
    lookup_field = 'asin'


class ProductReviewsView(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/products/{asin}/reviews/   -> reviews d'un produit, chacune avec son score
    """
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(
            product__asin=self.kwargs['asin']
        ).select_related('score').order_by('-posted_at')
