from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Product, Order, OrderItem, Address, Payment, User
from .forms import CustomUserChangeForm, CustomUserCreationForm

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

class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('email', 'is_admin', 'is_staff')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(User, UserAdmin)
