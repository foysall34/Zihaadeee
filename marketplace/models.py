from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = settings.AUTH_USER_MODEL

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    TYPE_CHOICES = [
        ('ebook', 'E-Book'),
        ('course', 'Course'),
        ('bundle', 'Bundle'),
        ('business', 'Business Tool'),
    ]

    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='product_thumbs/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    rating = models.FloatField(default=0.0)
    total_reviews = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.type})"

# Ebook specific
class Ebook(models.Model):
    product = models.OneToOneField(Product, related_name='ebook', on_delete=models.CASCADE)
    author = models.CharField(max_length=200)
    language = models.CharField(max_length=80, default='English')
    genre = models.CharField(max_length=120, blank=True)
    format = models.CharField(max_length=20, default='PDF')
    sample = models.FileField(upload_to='ebook_samples/', null=True, blank=True)
    file = models.FileField(upload_to='ebooks/', null=True, blank=True)

# Course specific
class Course(models.Model):
    product = models.OneToOneField(Product, related_name='course', on_delete=models.CASCADE)
    instructor = models.CharField(max_length=200)
    level = models.CharField(max_length=50, choices=[('beginner','Beginner'),('intermediate','Intermediate'),('advanced','Advanced')], default='beginner')
    duration = models.CharField(max_length=50, blank=True)  # e.g. "6h 30m"
    lessons_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.title} by {self.instructor}"

# Bundle specific
class Bundle(models.Model):
    product = models.OneToOneField(Product, related_name='bundle', on_delete=models.CASCADE)
    ebooks = models.ManyToManyField(Ebook, blank=True, related_name='bundles')
    courses = models.ManyToManyField(Course, blank=True, related_name='bundles')
    discount_percent = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    @property
    def original_price(self):
        total = Decimal('0.00')
        for ebook in self.ebooks.all():
            total += ebook.product.price
        for course in self.courses.all():
            total += course.product.price
        return total

    @property
    def discounted_price(self):
        orig = self.original_price
        discount = (orig * Decimal(self.discount_percent)) / Decimal(100)
        return orig - discount

# Business Tool model
class BusinessTool(models.Model):
    product = models.OneToOneField(Product, related_name='business_tool', on_delete=models.CASCADE)
    tags = models.JSONField(default=list, blank=True)  # or ManyToMany to a Tag model

# Review / Rating
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','product')

# Orders
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('paid','Paid'),
        ('failed','Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
