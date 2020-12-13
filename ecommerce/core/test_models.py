from django.contrib.auth.models import User
from django.test import TestCase
from .models import Product, Order, OrderItem, Address, Payment

class ProductTests(TestCase):
    def setUp(self):
        Product.objects.create(title='Product title 1', description='Product description 1', price=53.5, category='Computers')
            
    def test_product_name_is_product_title(self):
        product = Product.objects.get(id=1)
        expected_object_name = f'{product.title}'
        self.assertEqual(str(product), expected_object_name)
        
    def test_product_get_absolute_url(self):
        product = Product.objects.get(id=1)
        self.assertEqual(product.get_absolute_url(), '/detail/1/')
        
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
        
    def test_order_name(self):
        order = Order.objects.get(id=1)
        expected_name = f'Order #{order.pk}'
        self.assertEqual(order.__str__(), expected_name)
        
    def test_order_total_price_is_sum_of_order_items_price_with_two_order_items(self):
        order = Order.objects.get(id=1)
        product_1 = Product.objects.get(id=1)
        product_2 = Product.objects.get(id=2)
        OrderItem.objects.create(item=product_1, order=order, quantity=3)
        OrderItem.objects.create(item=product_2, order=order, quantity=1)
        expected_total_price = 0
        for order_item in OrderItem.objects.filter(order=order):
            expected_total_price += order_item.total_price
        self.assertEqual(order.total_price, expected_total_price)
        
    def test_order_total_price_is_sum_of_order_items_price_with_zero_order_items(self):
        order = Order.objects.get(id=1)
        expected_total_price = 0
        self.assertEqual(order.total_price, expected_total_price)
    
class OrderItemTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser1', password='pass123')
        user.save()
        
        product = Product.objects.create(title='Product title 1', description='Product description 1', price=53.5, category='Computers')
        product.save()
        
        order = Order.objects.create(user=user, order_number="10")
        order.save()
        
    def test_order_item_name(self):
        order = Order.objects.get(id=1)
        product = Product.objects.get(id=1)
        order_item = OrderItem.objects.create(item=product, order=order)
        expected_name = f'{order_item.quantity} of {order_item.item.title}'
        self.assertEqual(str(order_item), expected_name)
        
    def test_order_item_total_price_with_zero_quantity(self):
        order = Order.objects.get(id=1)
        product = Product.objects.get(id=1)
        order_item = OrderItem.objects.create(item=product, order=order, quantity=0)
        expected_total_price = 0
        self.assertEqual(order_item.total_price, expected_total_price)
        
    def test_order_item_total_price_with_one_quantity(self):
        order = Order.objects.get(id=1)
        product = Product.objects.get(id=1)
        order_item = OrderItem.objects.create(item=product, order=order, quantity=1)
        expected_total_price = order_item.item.price
        self.assertEqual(order_item.total_price, expected_total_price)
        
    def test_order_item_total_price_with_ten_quantity(self):
        order = Order.objects.get(id=1)
        product = Product.objects.get(id=1)
        order_item = OrderItem.objects.create(item=product, order=order, quantity=10)
        expected_total_price = 10 * order_item.item.price
        self.assertEqual(order_item.total_price, expected_total_price)    
        
class AddressTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser1', password='pass123')
        user.save()
        
        Address.objects.create(user=user, name='John Doe', country='NZ', province='Eastern Cape', zip_code='00408', city='Big City', suburb='Small suburb', street_address='50 Big Street', mobile_number='0723518979')
        
    def test_address_name(self):
        address = Address.objects.get(id=1)
        expected_name = f'{address.name} at {address.street_address}'
        self.assertEqual(str(address), expected_name)
        
        # TODO province categories


class PaymentTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser1', password='pass123')
        user.save()
        
        address = Address.objects.create(user=user, name='John Doe', country='NZ', province='Eastern Cape', zip_code='00408', city='Big City', suburb='Small suburb', street_address='50 Big Street', mobile_number='0723518979')
        address.save()
        
        order = Order.objects.create(user=user, order_number="10")
        order.save()
        
    def test_payment_name(self):
        address = Address.objects.get(id=1)
        order = Order.objects.get(id=1)
        payment = Payment.objects.create(amount=50, address=address, order=order)
        payment.save()
        expected_name = f"{payment.item_name} R{payment.amount}"
        self.assertEqual(str(payment), expected_name)
        
    def test_payment_item_name(self):
        address = Address.objects.get(id=1)
        order = Order.objects.get(id=1)
        payment = Payment.objects.create(amount=50, address=address, order=order)
        payment.save()
        expected_item_name = f"Order #{order.id}"
        self.assertEqual(payment.item_name, expected_item_name)
        
        # TODO amount can't be negative
        
        