from django.contrib import admin

# Register your models here.
from .models import Product, Order, OrderItem, Address, Payment

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Address)
admin.site.register(Payment)
