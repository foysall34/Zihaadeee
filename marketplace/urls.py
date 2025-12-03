from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, EbookListView, CourseListView, ProductDetailView, ReviewCreateView, CreateCheckoutSessionView, stripe_webhook

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')  # general product endpoints

urlpatterns = [
    path('', include(router.urls)),
    path('ebooks/', EbookListView.as_view(), name='ebook-list'),
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/review/', ReviewCreateView.as_view(), name='product-review'),
    path('stripe/create-checkout/', CreateCheckoutSessionView.as_view(), name='create-checkout'),
    path('stripe/webhook/', stripe_webhook, name='stripe-webhook'),
]
