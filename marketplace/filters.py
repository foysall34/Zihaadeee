import django_filters
from .models import Ebook, Course, Product

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')

    class Meta:
        model = Product
        fields = ['category', 'type', 'min_price', 'max_price', 'min_rating']

class EbookFilter(ProductFilter):
    author = django_filters.CharFilter(field_name='ebook__author', lookup_expr='icontains')
    language = django_filters.CharFilter(field_name='ebook__language', lookup_expr='iexact')
    genre = django_filters.CharFilter(field_name='ebook__genre', lookup_expr='icontains')

    class Meta(ProductFilter.Meta):
        model = Product
        fields = ProductFilter.Meta.fields + ['author','language','genre']

class CourseFilter(ProductFilter):
    instructor = django_filters.CharFilter(field_name='course__instructor', lookup_expr='icontains')
    level = django_filters.CharFilter(field_name='course__level', lookup_expr='iexact')

    class Meta(ProductFilter.Meta):
        model = Product
        fields = ProductFilter.Meta.fields + ['instructor','level']
