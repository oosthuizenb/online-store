from django import setup
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Product, Order, OrderItem, Address, Payment

class IndexTest(TestCase):
    def test_view_url_exists(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        
    def test_context_product_count_with_three_products(self):
        for i in range(3):
            Product.objects.create(title=f'Product title {i}', description=f'Product description {i}', price=50, category='CP')
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('products' in response.context)
        self.assertEqual(len(response.context['products']), 3)
        
    def test_context_product_count_with_zero_products(self):
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('products' in response.context)
        self.assertEqual(len(response.context['products']), 0)
        
    def test_context_contains_user(self):
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('user' in response.context)

class ProductDetailTest(TestCase):
    pass            