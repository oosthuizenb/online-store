from django.contrib.auth.models import User
from django.test import TestCase
from .models import Product, Order, OrderItem, Address, Payment

class ProductTests(TestCase):
    def setUp(self):
        Product.objects.create(title='Product title 1', description='Product description 1', price=53.5, category='CP')
        Product.objects.create(title='Product title 2', description='Product description 2', price=10, category='BK')
        
            
    def test_product_name_is_product_title(self):
        product = Product.objects.get(id=1)
        expected_object_name = 'Product title 1' # TODO hard code these values?
        self.assertEqual(str(product), expected_object_name)
        
    def test_product_get_absolute_url(self):
        product = Product.objects.get(id=1)
        self.assertEqual(product.get_absolute_url(), '/detail/1/')
        
    def test_product_category_cp_is_computers(self):
        product = Product.objects.get(id=1)
        expected_category = 'Computers'
        self.assertEqual(product.get_category_display(), expected_category)
        
    def test_product_category_bk_is_book(self):
        product = Product.objects.get(id=2)
        expected_category = 'Book'
        self.assertEqual(product.get_category_display(), expected_category)
        
    # TODO test that there is actually an image uploaded
    # TODO test publish_date is equal to date instance was created
        
class OrderTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser1', password='pass123')
        user.save()
        
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=53.5, category='CP')
        product_1.save()
        product_2 = Product.objects.create(title='Product title 2', description='Product description 2', price=100.0, category='CG')
        product_2.save()
        
        order = Order.objects.create(user=user, order_number="10")
        order.save()
        
    def test_order_name(self):
        order = Order.objects.get(id=1)
        expected_name = f'Order #1'
        self.assertEqual(str(order), expected_name)
        
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
        
    def test_order_total_price_is_sum_of_order_items_price_with_one_order_items(self):
        order = Order.objects.get(id=1)
        product_1 = Product.objects.get(id=1)
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        expected_total_price = 53.5
        self.assertEqual(order.total_price, expected_total_price)
        
    def test_order_total_price_is_sum_of_order_items_price_with_zero_order_items(self):
        order = Order.objects.get(id=1)
        expected_total_price = 0
        self.assertEqual(order.total_price, expected_total_price)
        
    
class OrderItemTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser1', password='pass123')
        user.save()
        
        product = Product.objects.create(title='Product title 1', description='Product description 1', price=53.5, category='CP')
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
        expected_total_price = 53.5
        self.assertEqual(order_item.total_price, expected_total_price)
        
    def test_order_item_total_price_with_ten_quantity(self):
        order = Order.objects.get(id=1)
        product = Product.objects.get(id=1)
        order_item = OrderItem.objects.create(item=product, order=order, quantity=10)
        expected_total_price = 10 * 53.5
        self.assertEqual(order_item.total_price, expected_total_price)    
        
class AddressTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser1', password='pass123')
        user.save()
        
        Address.objects.create(user=user, name='John Doe', country='NZ', province='WC', zip_code='00408', city='Big City', suburb='Small suburb', street_address='50 Big Street', mobile_number='0723518979')
        Address.objects.create(user=user, name='John Doe', country='NZ', province='NC', zip_code='00408', city='Big City', suburb='Small suburb', street_address='50 Big Street', mobile_number='0723518979')
        Address.objects.create(user=user, name='John Doe', country='NZ', province='LM', zip_code='00408', city='Big City', suburb='Small suburb', street_address='50 Big Street', mobile_number='0723518979')
        
        
    def test_address_name(self):
        address = Address.objects.get(id=1)
        expected_name = 'John Doe at 50 Big Street'
        self.assertEqual(str(address), expected_name)
        
    def test_address_category_wc_is_western_cape(self):
        address = Address.objects.get(id=1)
        expected_category = 'Western Cape'
        self.assertEqual(address.get_province_display(), expected_category)
        
    def test_address_category_nc_is_northern_cape(self):
        address = Address.objects.get(id=2)
        expected_category = 'Northern Cape'
        self.assertEqual(address.get_province_display(), expected_category)
        
    def test_address_category_lm_is_limpopo(self):
        address = Address.objects.get(id=3)
        expected_category = 'Limpopo'
        self.assertEqual(address.get_province_display(), expected_category)


class PaymentTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser1', password='pass123')
        user.save()
        
        address = Address.objects.create(user=user, name='John Doe', country='NZ', province='EC', zip_code='00408', city='Big City', suburb='Small suburb', street_address='50 Big Street', mobile_number='0723518979')
        address.save()
        
        order = Order.objects.create(user=user, order_number="10")
        order.save()
        
    def test_payment_name(self):
        address = Address.objects.get(id=1)
        order = Order.objects.get(id=1)
        payment = Payment.objects.create(amount=50, address=address, order=order)
        payment.save()
        expected_name = "Order #1 R50"
        self.assertEqual(str(payment), expected_name)
        
    def test_payment_item_name(self):
        address = Address.objects.get(id=1)
        order = Order.objects.get(id=1)
        payment = Payment.objects.create(amount=50, address=address, order=order)
        payment.save()
        expected_item_name = "Order #1"
        self.assertEqual(payment.item_name, expected_item_name)
        
    def test_payment_status_default_is_processing(self):
        address = Address.objects.get(id=1)
        order = Order.objects.get(id=1)
        payment = Payment.objects.create(amount=50, address=address, order=order)
        payment.save()
        expected_payment_status = 'PROCESSING'
        self.assertEqual(payment.get_payment_status_display(), expected_payment_status)
        
        
        
# TODO model baker..
# TODO test one-to-many relationships
# TODO test verbose labels
# TODO test max_length and other field attribute designs..