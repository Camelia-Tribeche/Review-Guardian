from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductReviewsView

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = router.urls + [
    path('products/<str:asin>/reviews/', ProductReviewsView.as_view({'get': 'list'}), name='product-reviews'),
]
