from rest_framework import serializers
from .models import Product, Category, Ebook, Course, Bundle, BusinessTool, Review, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','slug','icon']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = ['id','type','title','slug','description','thumbnail','price','rating','total_reviews','category','created_at','is_active']

class EbookSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = Ebook
        fields = ['product','author','language','genre','format','sample','file']

class CourseSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = Course
        fields = ['product','instructor','level','duration','lessons_count']

class BundleSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    ebooks = EbookSerializer(many=True, read_only=True)
    courses = CourseSerializer(many=True, read_only=True)
    class Meta:
        model = Bundle
        fields = ['product','ebooks','courses','discount_percent','original_price','discounted_price']

class BusinessToolSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = BusinessTool
        fields = ['product','tags']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Review
        fields = ['id','user','product','rating','comment','created_at']
        read_only_fields = ['user','created_at']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['product','unit_price','quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id','user','stripe_session_id','total_amount','status','created_at','paid_at','items']
        read_only_fields = ['status','created_at','paid_at','stripe_session_id']
