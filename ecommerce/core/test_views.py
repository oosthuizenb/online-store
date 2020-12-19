from django import setup
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Product, Order, OrderItem, Address, Payment
from .forms import RegisterForm

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
    def test_view_url_exists(self):
        Product.objects.create(title='Product title', description='Product description', price=50, category='CP')
        response = self.client.get('/detail/1/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        Product.objects.create(title='Product title', description='Product description', price=50, category='CP')
        response = self.client.get(reverse('core:product-detail', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        Product.objects.create(title='Product title', description='Product description', price=50, category='CP')
        response = self.client.get(reverse('core:product-detail', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/product_detail.html')

    def test_context_with_one_product(self):
        Product.objects.create(title='Product title', description='Product description', price=50, category='CP')
        response = self.client.get(reverse('core:product-detail', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('product' in response.context)
        self.assertTrue(isinstance(response.context['product'], Product))

    def test_404_response_with_no_product(self):
        response = self.client.get(reverse('core:product-detail', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 404)

class RegisterTest(TestCase):
    def test_view_url_exists(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('core:register'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('core:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_context_contains_register_form_with_get_request(self):
        response = self.client.get(reverse('core:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue(isinstance(response.context['form'], RegisterForm))

    def test_context_contains_register_form_with_post_request(self):
        response = self.client.post(reverse('core:register'), {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue(isinstance(response.context['form'], RegisterForm))

    def test_post_form_valid_with_valid_data_and_redirects_with_success_message(self):
        response = self.client.post(reverse('core:register'), {
            'email': 'testuser@gmail.com',
            'password': 'test',
            'password_confirm': 'test'
        }, follow=True)
        self.assertRedirects(response, reverse('core:index'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'Your account has been registered.')

    def test_post_form_with_valid_data_creates_user(self):
        response = self.client.post(reverse('core:register'), {
            'email': 'testuser@gmail.com',
            'password': 'test',
            'password_confirm': 'test'
        })
        self.assertRedirects(response, reverse('core:index'))
        self.assertEqual(User.objects.filter(username='testuser@gmail.com').count(), 1)
        self.assertEqual(User.objects.all()[0].username, 'testuser@gmail.com')

    def test_post_form_invalid_with_empty_data(self):
        response = self.client.post(reverse('core:register'), {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue(isinstance(response.context['form'], RegisterForm))
        self.assertFalse(response.context['form'].is_valid())

    def test_post_form_invalid_with_existing_user(self):
        User.objects.create_user(username='testuser@gmail.com', password='1X<ISRUkw+tuK')
        response = self.client.post(reverse('core:register'), {
            'email': 'testuser@gmail.com',
            'password': 'test',
            'password_confirm': 'test'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue(isinstance(response.context['form'], RegisterForm))
        self.assertFormError(response, 'form', 'email', 'The username already exists.')

    def test_post_form_invalid_with_non_matching_passwords(self):
        response = self.client.post(reverse('core:register'), {
            'email': 'testuser@gmail.com',
            'password': 'test',
            'password_confirm': 'test_not'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], RegisterForm)
        self.assertFormError(response, 'form', None, 'Passwords must match.')

    def test_user_creation_fails_with_invalid_form(self):
        response = self.client.post(reverse('core:register'), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], RegisterForm)
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(User.objects.all().count(), 0)

    def test_validation_error_with_empty_username(self):
        response = self.client.post(reverse('core:register'), {
            'email': '',
            'password': 'test',
            'password_confirm': 'test_not'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], RegisterForm)
        self.assertFormError(response, 'form', 'email', 'This field is required.')

    def test_validation_error_with_empty_password(self):
        response = self.client.post(reverse('core:register'), {
            'email': 'test@gmail.com',
            'password': '',
            'password_confirm': 'test_not'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], RegisterForm)
        self.assertFormError(response, 'form', 'password', 'This field is required.')

    def test_correct_template_and_error_message_with_invalid_form(self):
        response = self.client.post(reverse('core:register'), {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], RegisterForm)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'danger')
        self.assertEqual(message.message, 'Please fill in the form with valid information.')

    def test_view_405_with_put_request(self):
        response = self.client.put(reverse('core:register'))
        self.assertEqual(response.status_code, 405)

class ViewCartTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='pass')

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 302)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('core:cart'))
        self.assertRedirects(response, reverse('core:login') + '?next=/cart/')

    def test_uses_correct_template_if_logged_in(self):
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/cart.html')

    def test_context_contains_order_items_with_one_order_item(self):
        user = User.objects.all()[0]
        order = Order.objects.create(user=user, order_number="1")
        order.save()
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=53.5, category='CP')
        product_1.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('order_items', response.context)
        self.assertIsInstance(response.context['order_items'][0], OrderItem)
        self.assertEqual(len(response.context['order_items']), 1)

    def test_context_contains_order_items_with_three_order_items(self):
        user = User.objects.all()[0]
        order = Order.objects.create(user=user, order_number="1")
        order.save()
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        product_2 = Product.objects.create(title='Product title 2', description='Product description 2', price=1005, category='BK')
        product_2.save()
        product_3 = Product.objects.create(title='Product title 3', description='Product description 3', price=530.5, category='CG')
        product_3.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        OrderItem.objects.create(item=product_2, order=order, quantity=1)
        OrderItem.objects.create(item=product_3, order=order, quantity=1)
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('order_items', response.context)
        self.assertIsInstance(response.context['order_items'][0], OrderItem)
        self.assertEqual(len(response.context['order_items']), 3)

    def test_context_does_not_contain_order_items_with_no_order(self):
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('order_items', response.context)

    def test_context_does_not_contain_order_items_with_order_but_zero_order_items(self):
        user = User.objects.all()[0]
        order = Order.objects.create(user=user, order_number="1")
        order.save()
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('order_items', response.context)


class AddToCartTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='testuser1', password='pass')

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 302)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1}))
        self.assertRedirects(response, reverse('core:login') + '?next=/cart-add/1/')

    def test_redirect_if_logged_in(self):
        Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1}))
        self.assertRedirects(response, reverse('core:cart'))

    def test_404_if_product_does_not_exist(self):
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_order_item_creation_with_order_and_zero_order_items(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user, order_number="1")
        order.save()
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1}), follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item has been added to your cart.')
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(OrderItem.objects.all().count(), 1)

    def test_new_order_item_quantity_is_one_with_existing_order(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user, order_number="1")
        order.save()
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1}))
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(OrderItem.objects.all()[0].quantity, 1)

    def test_order_item_quantity_is_two_with_order_and_existing_order_item_quantity_of_one(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user, order_number="1")
        order.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1}), follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item quantity in your cart has been updated.')
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(OrderItem.objects.all()[0].quantity, 2)

    def test_order_creation_when_no_order_exists(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1}))
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(Order.objects.all().count(), 1)

    def test_order_item_creation_when_no_order_exists(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1}), follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item has been added to your cart.')
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(OrderItem.objects.all().count(), 1)

    def test_new_order_item_is_related_to_active_order(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user, order_number="1")
        order.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1}), follow=True)
        self.assertRedirects(response, reverse('core:cart'))
        self.assertTrue(OrderItem.objects.all()[0].order.is_active)

class RemoveFromCartTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='testuser1', password='pass')

    def test_view_url_accessible_by_name_not_logged_in(self):
        response = self.client.get(reverse('core:cart-remove', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 302)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('core:cart-remove', kwargs={'product_id': 1}))
        self.assertRedirects(response, reverse('core:login') + '?next=/cart-remove/1/')

    def test_redirect_if_logged_in_and_order_with_order_item_exists(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user, order_number="1")
        order.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-remove', kwargs={'product_id': 1}))
        self.assertRedirects(response, reverse('core:cart'))

    def test_404_if_product_does_not_exist(self):
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-remove', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_404_if_order_does_not_exist(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-remove', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_404_if_order_exists_but_order_item_does_not(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user, order_number="1")
        order.save()
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-remove', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_order_item_delete_with_order_and_order_item(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user, order_number="1")
        order.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        login = self.client.login(username='testuser1', password='pass')
        self.assertEqual(order.orderitem_set.count(), 1)
        response = self.client.get(reverse('core:cart-remove', kwargs={'product_id': 1}), follow=True)
        self.assertEqual(order.orderitem_set.count(), 0)
        self.assertRedirects(response, reverse('core:cart'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item has been removed from your cart.')

class RemoveSingleFromCartTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='testuser1', password='pass')

    def test_view_url_accessible_by_name_not_logged_in(self):
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 302)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}))
        self.assertRedirects(response, reverse('core:login') + '?next=/cart-remove-single/1/')

    def test_redirect_if_logged_in_and_order_with_order_item_exists(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user, order_number="1")
        order.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}))
        self.assertRedirects(response, reverse('core:cart'))

    def test_404_if_product_does_not_exist(self):
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_404_if_order_does_not_exist(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_404_if_order_exists_but_order_item_does_not(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user, order_number="1")
        order.save()
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_order_item_delete_with_order_and_order_item_quantity_one(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user, order_number="1")
        order.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        login = self.client.login(username='testuser1', password='pass')
        self.assertEqual(order.orderitem_set.count(), 1)
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}), follow=True)
        self.assertEqual(order.orderitem_set.count(), 0)
        self.assertRedirects(response, reverse('core:cart'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item has been removed from your cart.')

    def test_order_item_exists_after_update_with_order_and_order_item_quantity_two(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user, order_number="1")
        order.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=2)
        login = self.client.login(username='testuser1', password='pass')
        self.assertEqual(order.orderitem_set.count(), 1)
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}), follow=True)
        self.assertEqual(order.orderitem_set.count(), 1)
        self.assertRedirects(response, reverse('core:cart'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item quantity has been updated.')

    def test_order_item_quantity_is_one_after_update_with_order_and_order_item_quantity_two(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user, order_number="1")
        order.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=2)
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}), follow=True)
        self.assertEqual(order.orderitem_set.all()[0].quantity, 1)
        self.assertRedirects(response, reverse('core:cart'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item quantity has been updated.')

class CheckoutTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='testuser1', password='pass')

    def test_view_url_accessible_by_name_not_logged_in(self):
        response = self.client.get(reverse('core:checkout'))
        self.assertEqual(response.status_code, 302)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('core:checkout'))
        self.assertRedirects(response, reverse('core:login') + '?next=/checkout/')

    def test_404_if_order_does_not_exist(self):
        login = self.client.login(username='testuser1', password='pass')
        response = self.client.get(reverse('core:checkout'))
        self.assertEqual(response.status_code, 404)

    # order exists but no order items GET/POST(redirect to cart with message), 
    # GET: order exist with order items context contains form, context contains existing_addresses with count 0, context contains existing_addresses with count 1, 
    # POST: address_id is None (form does not contain addresses) 
    # then test valid->
    # address save->
    # address related to user,
    # invalid->
    # form with each error->
    # existing_addresses. 
    # address_id exists test get/404. 
    # Test payment creation with valid and invalid data. 
    # Test payment data fields(consider payment form for validation). 
    # Test signature string valid/invalid cases. 
    # Test that signature is part of payment_data. 
    # Test context contains payment_data, 
    # context contains payfast url.
    