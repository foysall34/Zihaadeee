from django.contrib import admin

from .models import  Product, Category , OrderItem , Order, Bundle , Ebook ,Course



admin.site.register(Course)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Bundle)
admin.site.register(Ebook)
admin.site.register(Category)
