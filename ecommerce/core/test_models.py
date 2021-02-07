from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from .models import Product, Order, OrderItem, Address, Payment, Review

class ProductTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=53.5, category='CP')
        cls.product_2 = Product.objects.create(title='Product title 2', description='Product description 2', price=10, category='BK')
        cls.product_1.save()
        cls.product_2.save()
        
            
    def test_product_name_is_product_title(self):
        expected_object_name = 'Product title 1' # TODO hard code these values?
        self.assertEqual(str(self.product_1), expected_object_name)
        
    def test_product_get_absolute_url(self):
        self.assertEqual(self.product_1.get_absolute_url(), '/detail/1/')
        
    def test_product_category_cp_is_computers(self):
        expected_category = 'Computers'
        self.assertEqual(self.product_1.get_category_display(), expected_category)
        
    def test_product_category_bk_is_book(self):
        expected_category = 'Book'
        self.assertEqual(self.product_2.get_category_display(), expected_category)
        
    # TODO test that there is actually an image uploaded
    # TODO test publish_date is equal to date instance was created
        
class OrderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='pass123')
        cls.user_2 = User.objects.create_user(username='testuser2', password='pass123')


        cls.product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=53.5, category='CP')
        cls.product_1.save()
        cls.product_2 = Product.objects.create(title='Product title 2', description='Product description 2', price=100.0, category='CG')
        cls.product_2.save()
        
        cls.order = Order.objects.create(user=cls.user)
        cls.order.save()

    def setUp(self):
        self.factory = RequestFactory()

        
    def test_order_name(self):
        expected_name = f'Order #1'
        self.assertEqual(str(self.order), expected_name)
        
    def test_order_total_price_is_sum_of_order_items_price_with_two_order_items(self):
        OrderItem.objects.create(item=self.product_1, order=self.order, quantity=3)
        OrderItem.objects.create(item=self.product_2, order=self.order, quantity=1)
        expected_total_price = 0
        for order_item in OrderItem.objects.filter(order=self.order):
            expected_total_price += order_item.total_price
        self.assertEqual(self.order.total_price, expected_total_price)
        
    def test_order_total_price_is_sum_of_order_items_price_with_one_order_items(self):
        OrderItem.objects.create(item=self.product_1, order=self.order, quantity=1)
        expected_total_price = 53.5
        self.assertEqual(self.order.total_price, expected_total_price)
        
    def test_order_total_price_is_sum_of_order_items_price_with_zero_order_items(self):
        expected_total_price = 0
        self.assertEqual(self.order.total_price, expected_total_price)

    # TODO: Test following cases for function return values and correct session order id.
    # guest, no active order, no guest order
    def test_guest_order_new_or_get_returns_new_order_with_no_session_order_id(self):
        request = self.factory.get(reverse('core:index'))
        request.user = AnonymousUser()
        request.session = self.client.session
        order, new_obj = Order.objects.new_or_get(request)
        self.assertTrue(new_obj)
        self.assertIsInstance(order, Order)

    def test_guest_order_new_or_get_adds_session_order_id_no_session_order_id(self):
        request = self.factory.get(reverse('core:index'))
        request.user = AnonymousUser()
        request.session = self.client.session
        order, new_obj = Order.objects.new_or_get(request)
        self.assertEqual(request.session['order_id'], order.id)      
    
    # guest, no active order, existing guest order
    def test_guest_order_new_or_get_returns_guest_order_with_session_order_id(self):
        test_order = Order.objects.create()
        test_order.save()
        request = self.factory.get(reverse('core:index'))
        request.user = AnonymousUser()
        request.session = self.client.session
        request.session['order_id'] = test_order.id
        request.session.save()
        order, new_obj = Order.objects.new_or_get(request)
        self.assertFalse(new_obj)
        self.assertIsInstance(order, Order)
        self.assertEqual(order.id, test_order.id)

    def test_guest_order_new_or_get_keeps_session_order_id_with_session_order_id(self):
        test_order = Order.objects.create()
        test_order.save()
        request = self.factory.get(reverse('core:index'))
        request.user = AnonymousUser()
        request.session = self.client.session
        request.session['order_id'] = test_order.id
        request.session.save()
        order, new_obj = Order.objects.new_or_get(request)
        self.assertEqual(request.session['order_id'], test_order.id) 

    # auth, no active order, no guest order
    def test_auth_order_new_or_get_returns_new_order_with_no_session_order_id_and_no_active_order(self):
        request = self.factory.get(reverse('core:index'))
        request.user = self.user_2
        request.session = self.client.session
        order, new_obj = Order.objects.new_or_get(request)
        self.assertTrue(new_obj)
        self.assertIsInstance(order, Order)

    def test_auth_order_new_or_get_adds_session_order_id_with_no_session_order_id_and_no_active_order(self):
        request = self.factory.get(reverse('core:index'))
        request.user = self.user_2
        request.session = self.client.session
        order, new_obj = Order.objects.new_or_get(request)
        self.assertEqual(request.session['order_id'], order.id)

    def test_auth_order_new_or_get_relates_user_with_no_session_order_id_and_no_active_order(self):
        request = self.factory.get(reverse('core:index'))
        request.user = self.user_2
        request.session = self.client.session
        order, new_obj = Order.objects.new_or_get(request)
        self.assertEqual(self.user_2, order.user)

    # auth, existing active order, no guest order
    def test_auth_order_new_or_get_returns_active_order_with_no_session_order_id_and_active_order(self):
        test_order = Order.objects.create(user=self.user_2)
        test_order.save()
        request = self.factory.get(reverse('core:index'))
        request.user = self.user_2
        request.session = self.client.session
        order, new_obj = Order.objects.new_or_get(request)
        self.assertFalse(new_obj)
        self.assertIsInstance(order, Order)
        self.assertEqual(test_order, order)

    def test_auth_order_new_or_get_adds_session_order_id_with_no_session_order_id_and_active_order(self):
        test_order = Order.objects.create(user=self.user_2)
        test_order.save()
        request = self.factory.get(reverse('core:index'))
        request.user = self.user_2
        request.session = self.client.session
        order, new_obj = Order.objects.new_or_get(request)
        self.assertEqual(request.session['order_id'], test_order.id)

    # auth, no active order, existing guest order
    def test_auth_order_new_or_get_returns_guest_order_with_session_order_id_and_no_active_order(self):
        test_order = Order.objects.create()
        test_order.save()
        request = self.factory.get(reverse('core:index'))
        request.user = self.user_2
        request.session = self.client.session
        request.session['order_id'] = test_order.id
        request.session.save()
        order, new_obj = Order.objects.new_or_get(request)
        self.assertFalse(new_obj)
        self.assertIsInstance(order, Order)
        self.assertEqual(test_order, order)

    def test_auth_order_new_or_get_keeps_session_order_id_with_session_order_id_and_no_active_order(self):
        test_order = Order.objects.create()
        test_order.save()
        request = self.factory.get(reverse('core:index'))
        request.user = self.user_2
        request.session = self.client.session
        request.session['order_id'] = test_order.id
        request.session.save()
        order, new_obj = Order.objects.new_or_get(request)
        self.assertEqual(request.session['order_id'], test_order.id)

    def test_auth_order_new_or_get_relates_user_with_session_order_id_and_no_active_order(self):
        test_order = Order.objects.create()
        test_order.save()
        request = self.factory.get(reverse('core:index'))
        request.user = self.user_2
        request.session = self.client.session
        request.session['order_id'] = test_order.id
        request.session.save()
        order, new_obj = Order.objects.new_or_get(request)
        self.assertEqual(self.user_2, order.user)

    # auth, existing active order, existing guest order
    def test_auth_order_new_or_get_returns_active_order_with_session_order_id_and_active_order(self):
        test_order = Order.objects.create()
        test_order.save()
        request = self.factory.get(reverse('core:index'))
        request.user = self.user
        request.session = self.client.session
        request.session['order_id'] = test_order.id
        request.session.save()
        order, new_obj = Order.objects.new_or_get(request)
        self.assertFalse(new_obj)
        self.assertIsInstance(order, Order)
        self.assertEqual(self.order, order)

    def test_auth_order_new_or_get_updates_session_order_id_with_session_order_id_and_active_order(self):
        test_order = Order.objects.create()
        test_order.save()
        request = self.factory.get(reverse('core:index'))
        request.user = self.user
        request.session = self.client.session
        request.session['order_id'] = test_order.id
        request.session.save()
        order, new_obj = Order.objects.new_or_get(request)
        self.assertEqual(request.session['order_id'], self.order.id)
        
    
class OrderItemTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser1', password='pass123')
        user.save()
        
        product = Product.objects.create(title='Product title 1', description='Product description 1', price=53.5, category='CP')
        product.save()
        
        order = Order.objects.create(user=user)
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
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='testuser1', password='pass123')
        user.save()
        address = Address.objects.create(user=user, name='John Doe', country='NZ', province='EC', zip_code='00408', city='Big City', suburb='Small suburb', street_address='50 Big Street', mobile_number='0723518979')
        address.save()
        order = Order.objects.create(user=user)
        order.save()
        cls.payment = Payment.objects.create(amount=50, address=address, order=order)
        cls.payment.save()
        
    def test_payment_name(self):
        expected_name = "Order #1 R50"
        self.assertEqual(str(self.payment), expected_name)
        
    def test_payment_item_name(self):
        expected_item_name = "Order #1"
        self.assertEqual(self.payment.item_name, expected_item_name)
        
    def test_payment_status_default_is_processing(self):
        expected_payment_status = 'PROCESSING'
        self.assertEqual(self.payment.get_status_display(), expected_payment_status)
        
        
        
# TODO model baker..
# TODO test one-to-many relationships
# TODO test verbose labels
# TODO test max_length and other field attribute designs..

class ReviewTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        user = User.objects.create_user(username='testuser1', password='pass123')
        user.save()
        product = Product.objects.create(title='Product title 1', description='Product description 1', price=1000.0, category='CP')
        product.save()
        cls.review = Review.objects.create(user=user, product=product, rating=1, content='Review content.')
        cls.review.save()

    def test_user_label(self):
        field_label = self.review._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_product_label(self):
        field_label = self.review._meta.get_field('product').verbose_name
        self.assertEqual(field_label, 'product')

    def test_rating_label(self):
        field_label = self.review._meta.get_field('rating').verbose_name
        self.assertEqual(field_label, 'rating')

    def test_content_label(self):
        field_label = self.review._meta.get_field('content').verbose_name
        self.assertEqual(field_label, 'content')

    def test_publish_date_label(self):
        field_label = self.review._meta.get_field('publish_date').verbose_name
        self.assertEqual(field_label, 'publish date')

    def test_review_name(self):
        self.assertEqual(str(self.review), f'{self.review.product} with rating of {self.review.rating}')
