from django.contrib import admin

# Register your models here.
from .models import Product, Order, OrderItem, Address, Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'status', 'refund')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'placement_date', 'is_active')

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'order')

class AddressAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'price', 'publish_date')

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment, PaymentAdmin)
