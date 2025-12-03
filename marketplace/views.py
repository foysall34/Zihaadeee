from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.conf import settings
from decimal import Decimal
import stripe
from .models import Category, Product, Ebook, Course, Bundle, BusinessTool, Review, Order, OrderItem
from .serializers import (CategorySerializer, ProductSerializer, EbookSerializer,
                          CourseSerializer, BundleSerializer, BusinessToolSerializer,
                          ReviewSerializer, OrderSerializer)
from .filters import EbookFilter, CourseFilter, ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters

stripe.api_key = settings.STRIPE_SECRET_KEY

# Basic ViewSets / Lists
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price','rating','created_at']

# Specific product endpoints using product type filtering
class EbookListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = EbookFilter
    search_fields = ['title','product__ebook__author']

    def get_queryset(self):
        return Product.objects.filter(type='ebook', is_active=True)

class CourseListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ['title','product__course__instructor']

    def get_queryset(self):
        return Product.objects.filter(type='course', is_active=True)

# Product detail by type
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    lookup_field = 'id'

# Reviews
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        product_id = self.request.data.get('product')
        product = get_object_or_404(Product, id=product_id)
        serializer.save(user=self.request.user, product=product)
        # Update product rating (simple recalculation)
        reviews = product.reviews.all()
        total = sum([r.rating for r in reviews])
        product.total_reviews = reviews.count()
        product.rating = (total / reviews.count()) if reviews.count() else 0
        product.save()

# Orders & stripe checkout
from rest_framework.views import APIView
class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Expected payload:
        {
            "items": [
                {"product_id": 1, "quantity": 1},
                ...
            ],
            "success_url": "https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
            "cancel_url": "https://example.com/cancel"
        }
        """
        data = request.data
        items = data.get('items', [])
        if not items:
            return Response({"detail":"No items provided"}, status=status.HTTP_400_BAD_REQUEST)

        line_items = []
        total_amount = Decimal('0.00')
        # create a pending order (optional: you can create after webhook)
        order = Order.objects.create(user=request.user, total_amount=0)

        for it in items:
            pid = it.get('product_id')
            qty = int(it.get('quantity', 1))
            product = get_object_or_404(Product, id=pid, is_active=True)
            unit_price = product.price
            total_amount += (unit_price * qty)
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product.title,
                        'description': product.description[:200],
                    },
                    'unit_amount': int(unit_price * 100), # cents
                },
                'quantity': qty
            })
            OrderItem.objects.create(order=order, product=product, unit_price=unit_price, quantity=qty)

        order.total_amount = total_amount
        order.save()


        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='payment',
                customer_email=request.user.email,  
                line_items=line_items,
                success_url=data.get('success_url'),
                cancel_url=data.get('cancel_url'),
                metadata={'order_id': str(order.id)},
            )
            order.stripe_session_id = session.id
            order.save()
            return Response({'checkout_session_id': session.id, 'checkout_url': session.url})

        except Exception as e:
            return Response({'error': str(e)}, status=500)




# webhook handler (set endpoint in stripe dashboard)
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        return Response(status=400)

    # handle the event types you care about
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)

    return Response(status=200)

def handle_checkout_session(session):
    # finalize order
    order_id = session.get('metadata', {}).get('order_id')
    if not order_id:
        return
    try:
        order = Order.objects.get(id=order_id)
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save()
        # grant access logic: depending on product.type -> create entitlements, send email, etc.
    except Order.DoesNotExist:
        return
