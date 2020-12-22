from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<int:product_id>/', views.product_detail, name='product-detail'),
    path('cart/', views.view_cart, name='cart'),
    path('cart-add/<int:product_id>/', views.add_to_cart, name='cart-add'),
    path('cart-remove/<int:product_id>/', views.remove_from_cart, name='cart-remove'),
    path('cart-remove-single/<int:product_id>/', views.remove_single_from_cart, name='cart-remove-single'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment-notify/', views.payment_notify, name='payment-notify'),
    path('payment-return/', views.payment_return, name='payment-return'),
    path('payment-cancel/', views.payment_cancel, name='payment-cancel'),
    path('register/', views.register, name ='register'),
    path('accounts/login/', auth_views.LoginView.as_view(authentication_form=CustomAuthenticationForm), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
]
