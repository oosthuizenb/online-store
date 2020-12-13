from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Product, Order, OrderItem, Address, Payment

class ProductTests(TestCase):
    def setUp(self):
        Product.objects.create(title='Product title 1', description='Product description 1', price=53.5, category='Computers')
            
    def test_product_str(self):
        """__str__() method returns the product title"""
        product = Product.objects.get(id=1)
        self.assertEqual(product.__str__(), product.title )
        
    def test_product_get_absolute_url(self):
        """get_absolute_url() method returns reverse of core:product-detail plus product id as a URL"""
        product = Product.objects.get(id=1)
        self.assertEqual(product.get_absolute_url(), reverse("core:product-detail", kwargs={"product_id": product.id}))
        
    # TODO write test for categories
    # TODO price can't be negative
    # TODO test that there is actually an image uploaded
    # TODO test publish_date is equal to date instance was created
        
class OrderTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser1', password='pass123')
        user.save()
        
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=53.5, category='Computers')
        product_1.save()
        product_2 = Product.objects.create(title='Product title 2', description='Product description 2', price=100.0, category='Clothing')
        product_2.save()
        
        order = Order.objects.create(user=user, order_number="10")
        order.save()
        
        OrderItem.objects.create(item=product_1, order=order, quantity=3)
        OrderItem.objects.create(item=product_2, order=order, quantity=1)
        
    def test_order_str(self):
        """__str__() method returns 'Order #{order.pk}' """
        order = Order.objects.get(id=1)
        self.assertEqual(order.__str__(), f'Order #{order.pk}')
        
    def test_order_total_price(self):
        """total_price property is equal to the sum of all the particular order's order items"""
        order = Order.objects.get(id=1)
        total_p = 0
        for order_item in OrderItem.objects.filter(order=order):
            total_p = total_p + order_item.total_price
        self.assertEqual(order.total_price, total_p)
    
    # TODO few more different use cases for total price with different amounts of products/order items..