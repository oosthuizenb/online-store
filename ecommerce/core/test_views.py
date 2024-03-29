import datetime
import hashlib
from urllib.parse import urlencode, quote_plus

from django import setup
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Product, Order, OrderItem, Address, Payment, Review
from .forms import AddressForm, RegisterForm, ReviewForm

User = get_user_model()

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

class ProductSearchTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Product.objects.create(title='Bike', description='Product Test', price=50, category='CP')
        Product.objects.create(title='Bicycle', description='Product Test 2', price=50, category='BK')
        Product.objects.create(title='Louis Vutton', description='Product Test 3', price=50, category='CG')
        Product.objects.create(title='Louis Vuttelli', description='Product Test 4', price=50, category='CG')
        Product.objects.create(title='louis Masciani', description='Product Test 5', price=50, category='CG')
        Product.objects.create(title='Communication device', description='Product Test 6', price=500.0, category='CG')

    def test_view_url_exists(self):
        response = self.client.get('/search/')
        self.assertEqual(response.status_code, 200)
        
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('core:search'))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('core:search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_search_with_part_title_one_matching_product(self):
        get_parameters = {'search': 'Bik'}
        response = self.client.get(reverse('core:search'), get_parameters)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertIn('products', response.context)
        self.assertEqual(len(response.context['products']), 1)
        self.assertIn(Product.objects.get(description='Product Test'), response.context['products'])

    def test_search_with_part_title_case_insensitive_one_matching_product(self):
        get_parameters = {'search': 'bik'}
        response = self.client.get(reverse('core:search'), get_parameters)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertIn('products', response.context)
        self.assertEqual(len(response.context['products']), 1)
        self.assertIn(Product.objects.get(description='Product Test'), response.context['products'])

    def test_search_with_matching_title_one_matching_product(self):
        get_parameters = {'search': 'Louis Vutton'}
        response = self.client.get(reverse('core:search'), get_parameters)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertIn('products', response.context)
        self.assertEqual(len(response.context['products']), 1)
        self.assertIn(Product.objects.get(description='Product Test 3'), response.context['products'])

    def test_search_with_matching_title_case_insensitive_one_matching_product(self):
        get_parameters = {'search': 'louis vutton'}
        response = self.client.get(reverse('core:search'), get_parameters)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertIn('products', response.context)
        self.assertEqual(len(response.context['products']), 1)
        self.assertIn(Product.objects.get(description='Product Test 3'), response.context['products'])

    def test_search_with_part_title_two_matching_products(self):
        get_parameters = {'search': 'louis vutt'}
        response = self.client.get(reverse('core:search'), get_parameters)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertIn('products', response.context)
        self.assertEqual(len(response.context['products']), 2)
        self.assertIn(Product.objects.get(description='Product Test 3'), response.context['products'])
        self.assertIn(Product.objects.get(description='Product Test 4'), response.context['products'])

    def test_search_with_part_title_case_insensitive_three_matching_products(self):
        get_parameters = {'search': 'louis'}
        response = self.client.get(reverse('core:search'), get_parameters)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertIn('products', response.context)
        self.assertEqual(len(response.context['products']), 3)
        self.assertIn(Product.objects.get(description='Product Test 3'), response.context['products'])
        self.assertIn(Product.objects.get(description='Product Test 4'), response.context['products'])
        self.assertIn(Product.objects.get(description='Product Test 5'), response.context['products'])

    def test_search_with_empty_string_returns_all_products(self):
        get_parameters = {'search': ''}
        response = self.client.get(reverse('core:search'), get_parameters)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertIn('products', response.context)
        self.assertEqual(len(response.context['products']), Product.objects.count())

    def test_search_with_spaces_in_string_returns_all_products(self):
        get_parameters = {'search': '  '}
        response = self.client.get(reverse('core:search'), get_parameters)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertIn('products', response.context)
        self.assertEqual(len(response.context['products']), Product.objects.count())

class ProductDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='testuser1@gmail.com', password='password123')

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

    def test_context_contains_unbound_review_form(self):
        Product.objects.create(title='Product title', description='Product description', price=50, category='CP')
        response = self.client.get(reverse('core:product-detail', kwargs={'product_id': 1}))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], ReviewForm)
        self.assertFalse(response.context['form'].is_bound)

    def test_context_contains_0_reviews(self):
        Product.objects.create(title='Product title', description='Product description', price=50, category='CP')
        response = self.client.get(reverse('core:product-detail', kwargs={'product_id': 1}))
        self.assertIn('reviews', response.context)
        self.assertEqual(len(response.context['reviews']), 0)

    def test_context_contains_2_reviews(self):
        product = Product.objects.create(title='Product title', description='Product description', price=50, category='CP')
        product.save()
        Review.objects.create(user=self.user, product=product, rating=1, content='Good stuff')
        Review.objects.create(user=self.user, product=product, rating=5, content='Good stuff 5')
        response = self.client.get(reverse('core:product-detail', kwargs={'product_id': 1}))
        self.assertIn('reviews', response.context)
        self.assertEqual(len(response.context['reviews']), 2)   
        self.assertIsInstance(response.context['reviews'][0], Review)

class ReviewSubmitTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='testuser1@gmail.com', password='password123')
        Product.objects.create(title='Product title', description='Product description', price=50.0, category='CP')
        Product.objects.create(title='Product title 2', description='Product description 2', price=500.0, category='CP')

    def test_view_url_accessible(self):
        response = self.client.post('/review-submit/1/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_accessible_by_name(self):
        response = self.client.post(reverse('core:review-submit', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 302)

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(reverse('core:review-submit', kwargs={'product_id': 1}))
        self.assertRedirects(response, reverse('core:login') + '?next=/review-submit/1/')

    def test_redirect_review_valid_rating_and_content(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:review-submit', kwargs={'product_id': 1}), {
            'rating': 2, 
            'content': 'Good one.'
        })
        self.assertEqual(Review.objects.count(), 1)
        self.assertRedirects(response, reverse('core:product-detail', kwargs={'product_id': 1}))

    def test_redirect_review_valid_rating_empty_content(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:review-submit', kwargs={'product_id': 1}), {
            'rating': 4, 
            'content': ''
        })
        self.assertEqual(Review.objects.count(), 1)
        self.assertRedirects(response, reverse('core:product-detail', kwargs={'product_id': 1}))

    def test_review_valid_product_relate(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:review-submit', kwargs={'product_id': 1}), {
            'rating': 3, 
            'content': 'Good product.'
        })
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.all()[0].product, Product.objects.get(pk=1))
        self.assertRedirects(response, reverse('core:product-detail', kwargs={'product_id': 1}))

    def test_review_valid_user_relate(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:review-submit', kwargs={'product_id': 1}), {
            'rating': 3, 
            'content': 'Good product.'
        })
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.all()[0].user, self.user)
        self.assertRedirects(response, reverse('core:product-detail', kwargs={'product_id': 1}))

    def test_review_valid_publish_date_is_today(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:review-submit', kwargs={'product_id': 1}), {
            'rating': 5, 
            'content': 'Good product.'
        })
        today = datetime.date.today()
        self.assertEqual(Review.objects.all()[0].publish_date, today)
        self.assertRedirects(response, reverse('core:product-detail', kwargs={'product_id': 1}))

    def test_review_invalid_empty_rating(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:review-submit', kwargs={'product_id': 1}), {
            'rating': '', 
            'content': ''
        })
        self.assertEqual(Review.objects.count(), 0)
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].is_bound)
        self.assertFalse(response.context['form'].is_valid())
        self.assertFormError(response, 'form', 'rating', 'This field is required.')

    def test_review_invalid_0_rating(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:review-submit', kwargs={'product_id': 1}), {
            'rating': 0, 
            'content': ''
        })
        self.assertEqual(Review.objects.count(), 0)
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].is_bound)
        self.assertFalse(response.context['form'].is_valid())
        self.assertFormError(response, 'form', 'rating', 'Rating must be in the range from 1 to 5.')

    def test_review_invalid_6_rating(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:review-submit', kwargs={'product_id': 1}), {
            'rating': 6, 
            'content': ''
        })
        self.assertEqual(Review.objects.count(), 0)
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].is_bound)
        self.assertFalse(response.context['form'].is_valid())
        self.assertFormError(response, 'form', 'rating', 'Rating must be in the range from 1 to 5.')

    def test_review_invalid_correct_template(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:review-submit', kwargs={'product_id': 1}), {
            'rating': 6, 
            'content': 'Good'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.count(), 0)
        self.assertTemplateUsed(response, 'core/product_detail.html')

    def test_404_product_does_not_exist(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:review-submit', kwargs={'product_id': 5}), {
            'rating': 5, 
            'content': 'test'
        })
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
            'password': 'testtesttest1',
            'password_confirm': 'testtesttest1'
        }, follow=True)
        self.assertRedirects(response, reverse('core:index'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'Your account has been registered.')

    def test_post_form_with_valid_data_creates_user(self):
        response = self.client.post(reverse('core:register'), {
            'email': 'testuser@gmail.com',
            'password': 'testtesttest1',
            'password_confirm': 'testtesttest1'
        })
        self.assertRedirects(response, reverse('core:index'))
        self.assertEqual(User.objects.filter(email='testuser@gmail.com').count(), 1)
        self.assertEqual(User.objects.all()[0].email, 'testuser@gmail.com')

    def test_post_form_invalid_with_empty_data(self):
        response = self.client.post(reverse('core:register'), {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue(isinstance(response.context['form'], RegisterForm))
        self.assertFalse(response.context['form'].is_valid())

    def test_post_form_invalid_with_existing_user(self):
        User.objects.create_user(email='testuser@gmail.com', password='1X<ISRUkw+tuK')
        response = self.client.post(reverse('core:register'), {
            'email': 'testuser@gmail.com',
            'password': 'testtesttest1',
            'password_confirm': 'testtesttest1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue(isinstance(response.context['form'], RegisterForm))
        self.assertFormError(response, 'form', 'email', 'The username already exists.')

    def test_post_form_invalid_with_non_matching_passwords(self):
        response = self.client.post(reverse('core:register'), {
            'email': 'testuser@gmail.com',
            'password': 'testtesttest1',
            'password_confirm': 'test_nottesttest1'
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
            'password': 'testtesttest1',
            'password_confirm': 'test_nottesttest1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], RegisterForm)
        self.assertFormError(response, 'form', 'email', 'This field is required.')

    def test_validation_error_with_empty_password(self):
        response = self.client.post(reverse('core:register'), {
            'email': 'test@gmail.com',
            'password': '',
            'password_confirm': 'test_nottesttest1'
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
        test_user1 = User.objects.create_user(email='testuser1@gmail.com', password='password123')

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template_if_not_logged_in(self):
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/cart.html')

    def test_uses_correct_template_if_logged_in(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/cart.html')

    def test_context_contains_order_items_with_one_order_item(self):
        user = User.objects.all()[0]
        order = Order.objects.create(user=user)
        order.save()
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=53.5, category='CP')
        product_1.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('order_items', response.context)
        self.assertIsInstance(response.context['order_items'][0], OrderItem)
        self.assertEqual(len(response.context['order_items']), 1)

    def test_context_contains_order_items_with_three_order_items(self):
        user = User.objects.all()[0]
        order = Order.objects.create(user=user)
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
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('order_items', response.context)
        self.assertIsInstance(response.context['order_items'][0], OrderItem)
        self.assertEqual(len(response.context['order_items']), 3)

    def test_context_does_not_contain_order_items_with_no_order(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('order_items', response.context)

    def test_context_does_not_contain_order_items_with_order_but_zero_order_items(self):
        user = User.objects.all()[0]
        order = Order.objects.create(user=user)
        order.save()
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('order_items', response.context)

    def test_context_contains_guest_order_items_with_one_order_item(self):
        order = Order.objects.create()
        order.save()
        session = self.client.session
        session['order_id'] = order.id
        session.save()
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=53.5, category='CP')
        product_1.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('order_items', response.context)
        self.assertIsInstance(response.context['order_items'][0], OrderItem)
        self.assertEqual(len(response.context['order_items']), 1)

    def test_context_contains_guest_order_items_with_three_order_items(self):
        order = Order.objects.create()
        order.save()
        session = self.client.session
        session['order_id'] = order.id
        session.save()
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        product_2 = Product.objects.create(title='Product title 2', description='Product description 2', price=1005, category='BK')
        product_2.save()
        product_3 = Product.objects.create(title='Product title 3', description='Product description 3', price=530.5, category='CG')
        product_3.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        OrderItem.objects.create(item=product_2, order=order, quantity=1)
        OrderItem.objects.create(item=product_3, order=order, quantity=1)
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('order_items', response.context)
        self.assertIsInstance(response.context['order_items'][0], OrderItem)
        self.assertEqual(len(response.context['order_items']), 3)

    def test_context_does_not_contain_guest_order_items_with_no_order(self):
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('order_items', response.context)

    def test_context_does_not_contain_guest_order_items_with_order_but_zero_order_items(self):
        order = Order.objects.create()
        order.save()
        session = self.client.session
        session['order_id'] = order.id
        session.save()
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('order_items', response.context)



class AddToCartTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        cls.product_1.save()        
        cls.test_user = User.objects.create_user(email='testuser1@gmail.com', password='password123')

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1, 'redirect_url': 'cart'}))
        self.assertEqual(response.status_code, 302)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get('/cart-add/1/cart/', follow=True)
        self.assertRedirects(response, reverse('core:cart'))

    def test_redirect_cart_if_logged_in(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get('/cart-add/1/cart/', follow=True)
        self.assertRedirects(response, reverse('core:cart'))

    def test_redirect_product_detail_if_not_logged_in(self):
        response = self.client.get(reverse('core:cart-add', kwargs={
            'product_id': 1,
            'redirect_url': 'product-detail',
            }))
        self.assertRedirects(response, reverse('core:product-detail', kwargs={'product_id': 1}))

    def test_redirect_product_detail_if_logged_in(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-add', kwargs={
            'product_id': 1,
            'redirect_url': 'product-detail',
            }))
        self.assertRedirects(response, reverse('core:product-detail', kwargs={'product_id': 1}))

    def test_404_if_product_does_not_exist_logged_in(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 2, 'redirect_url': 'cart'}))
        self.assertEqual(response.status_code, 404)

    def test_404_if_product_does_not_exist_not_logged_in(self):
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 2, 'redirect_url': 'cart'}))
        self.assertEqual(response.status_code, 404)    

    def test_guest_order_item_creation_with_order_and_zero_order_items(self):
        order = Order.objects.create()
        order.save()
        session = self.client.session
        session['order_id'] = 1
        session.save()
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1, 'redirect_url': 'cart'}), follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item has been added to your cart.')
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(OrderItem.objects.all().count(), 1)

    def test_guest_new_order_item_quantity_is_one_with_existing_order(self):
        order = Order.objects.create()
        order.save()
        session = self.client.session
        session['order_id'] = 1
        session.save()
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1, 'redirect_url': 'cart'}))
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(OrderItem.objects.all()[0].quantity, 1)

    def test_guest_order_item_quantity_is_two_with_order_and_existing_order_item_quantity_of_one(self):
        order = Order.objects.create()
        order.save()
        session = self.client.session
        session['order_id'] = 1
        session.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1, 'redirect_url': 'cart'}), follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item quantity in your cart has been updated.')
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(OrderItem.objects.all()[0].quantity, 2)

    def test_guest_order_creation_when_no_order_exists(self):
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1, 'redirect_url': 'cart'}))
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(Order.objects.all().count(), 1)

    def test_guest_order_item_creation_when_no_order_exists(self):
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1, 'redirect_url': 'cart'}), follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item has been added to your cart.')
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(OrderItem.objects.all().count(), 1)

    def test_guest_order_id_in_session_after_order_creation(self):
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1, 'redirect_url': 'cart'}), follow=True)
        session = self.client.session
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(session['order_id'], 1)

    def test_order_id_in_session_after_existing_order_update(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1, 'redirect_url': 'cart'}), follow=True)
        session = self.client.session
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(session['order_id'], 1)

    def test_guest_new_order_item_is_related_to_active_order(self):
        order = Order.objects.create()
        order.save()
        session = self.client.session
        session['order_id'] = 1
        session.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1, 'redirect_url': 'cart'}), follow=True)
        self.assertRedirects(response, reverse('core:cart'))
        self.assertTrue(OrderItem.objects.all()[0].order.is_active)

    def test_order_item_creation_with_order_and_zero_order_items(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1, 'redirect_url': 'cart'}), follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item has been added to your cart.')
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(OrderItem.objects.all().count(), 1)

    def test_new_order_item_quantity_is_one_with_existing_order(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1, 'redirect_url': 'cart'}))
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(OrderItem.objects.all()[0].quantity, 1)

    def test_order_item_quantity_is_two_with_order_and_existing_order_item_quantity_of_one(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1, 'redirect_url': 'cart'}), follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item quantity in your cart has been updated.')
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(OrderItem.objects.all()[0].quantity, 2)

    def test_order_creation_when_no_order_exists(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1, 'redirect_url': 'cart'}))
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(Order.objects.all().count(), 1)

    def test_order_item_creation_when_no_order_exists(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1, 'redirect_url': 'cart'}), follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item has been added to your cart.')
        self.assertRedirects(response, reverse('core:cart'))
        self.assertEqual(OrderItem.objects.all().count(), 1)

    def test_new_order_item_is_related_to_active_order(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-add', kwargs={'product_id': 1, 'redirect_url': 'cart'}), follow=True)
        self.assertRedirects(response, reverse('core:cart'))
        self.assertTrue(OrderItem.objects.all()[0].order.is_active)

class RemoveFromCartTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(email='testuser1@gmail.com', password='password123')

    def test_redirect_if_guest_and_order_with_order_item_exists(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create()
        order.save()
        session = self.client.session
        session['order_id'] = order.id
        session.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        response = self.client.get(reverse('core:cart-remove', kwargs={'product_id': 1}))
        self.assertRedirects(response, reverse('core:cart'))

    def test_redirect_if_logged_in_and_order_with_order_item_exists(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-remove', kwargs={'product_id': 1}))
        self.assertRedirects(response, reverse('core:cart'))

    def test_404_if_product_does_not_exist(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-remove', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_404_if_order_does_not_exist(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-remove', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_404_if_order_exists_but_order_item_does_not(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user)
        order.save()
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-remove', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_order_item_delete_with_order_and_order_item(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        self.assertEqual(order.orderitem_set.count(), 1)
        response = self.client.get(reverse('core:cart-remove', kwargs={'product_id': 1}), follow=True)
        self.assertEqual(order.orderitem_set.count(), 0)
        self.assertRedirects(response, reverse('core:cart'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item has been removed from your cart.')

    def test_guest_order_item_delete_with_order_and_order_item(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create()
        order.save()
        session = self.client.session
        session['order_id'] = order.id
        session.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
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
        cls.test_user = User.objects.create_user(email='testuser1@gmail.com', password='password123')

    def test_redirect_if_logged_in_and_order_with_order_item_exists(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}))
        self.assertRedirects(response, reverse('core:cart'))

    def test_redirect_if_not_logged_in_and_order_with_order_item_exists(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create()
        order.save()
        session = self.client.session
        session['order_id'] = order.id
        session.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}))
        self.assertRedirects(response, reverse('core:cart'))

    def test_404_if_product_does_not_exist(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_404_if_order_does_not_exist(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_404_if_order_exists_but_order_item_does_not(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user)
        order.save()
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_order_item_delete_with_order_and_order_item_quantity_one(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
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
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=2)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
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
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=2)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}), follow=True)
        self.assertEqual(order.orderitem_set.all()[0].quantity, 1)
        self.assertRedirects(response, reverse('core:cart'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item quantity has been updated.')

    def test_guest_order_item_delete_with_order_and_order_item_quantity_one(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create()
        order.save()
        session = self.client.session
        session["order_id"] = order.id
        session.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=1)
        self.assertEqual(order.orderitem_set.count(), 1)
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}), follow=True)
        self.assertEqual(order.orderitem_set.count(), 0)
        self.assertRedirects(response, reverse('core:cart'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item has been removed from your cart.')

    def test_guest_order_item_exists_after_update_with_order_and_order_item_quantity_two(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create()
        order.save()
        session = self.client.session
        session["order_id"] = order.id
        session.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=2)
        self.assertEqual(order.orderitem_set.count(), 1)
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}), follow=True)
        self.assertEqual(order.orderitem_set.count(), 1)
        self.assertRedirects(response, reverse('core:cart'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item quantity has been updated.')

    def test_guest_order_item_quantity_is_one_after_update_with_order_and_order_item_quantity_two(self):
        product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        product_1.save()
        order = Order.objects.create()
        order.save()
        session = self.client.session
        session["order_id"] = order.id
        session.save()
        OrderItem.objects.create(item=product_1, order=order, quantity=2)
        response = self.client.get(reverse('core:cart-remove-single', kwargs={'product_id': 1}), follow=True)
        self.assertEqual(order.orderitem_set.all()[0].quantity, 1)
        self.assertRedirects(response, reverse('core:cart'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, 'The item quantity has been updated.')

class CheckoutTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(email='testuser1@gmail.com', password='password123')
        cls.product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5, category='CP')
        cls.product_1.save()
        cls.product_2 = Product.objects.create(title='Product title 2', description='Product description 2', price=5, category='BK')
        cls.product_2.save()


    def test_view_url_accessible_by_name_not_logged_in(self):
        response = self.client.get(reverse('core:checkout'))
        self.assertEqual(response.status_code, 302)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('core:checkout'))
        self.assertRedirects(response, reverse('core:login') + '?next=/checkout/')

    def test_redirect_to_cart_if_order_does_not_exist(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:checkout'))
        self.assertRedirects(response, reverse('core:cart'))

    def test_redirect_to_cart_if_order_exists_but_no_order_items(self):
        order = Order.objects.create(user=self.test_user)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:checkout'))
        self.assertRedirects(response, reverse('core:cart'))

    def test_uses_correct_template(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/checkout.html')

    def test_context_contains_address_form_with_get(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], AddressForm)

    def test_address_form_is_unbound_with_get(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_bound)

    def test_context_contains_one_existing_address_with_get(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        Address.objects.create(user=self.test_user, name='John Doe', country='NZ', province='WC', zip_code='00408', city='Big City', suburb='Small suburb', street_address='50 Big Street', mobile_number='0723518979')
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('existing_addresses', response.context)
        self.assertEqual(len(response.context['existing_addresses']), 1)
        self.assertIsInstance(response.context['existing_addresses'][0], Address)

    def test_context_contains_zero_existing_address_with_get(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('existing_addresses', response.context)
        self.assertEqual(len(response.context['existing_addresses']), 0)

    def test_new_address_form_is_bound(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].is_bound)

    def test_correct_template_with_invalid_data(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('core/checkout.html')

    def test_new_address_form_invalid_with_empty_data(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertFormError(response, 'form', 'name', 'This field is required.')
        self.assertFormError(response, 'form', 'country', 'This field is required.')
        self.assertFormError(response, 'form', 'province', 'This field is required.')
        self.assertFormError(response, 'form', 'zip_code', 'This field is required.')
        self.assertFormError(response, 'form', 'city', 'This field is required.')
        self.assertFormError(response, 'form', 'street_address', 'This field is required.')
        self.assertFormError(response, 'form', 'mobile_number', 'This field is required.')

    def test_new_address_form_invalid_zip_code_non_digits(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {'zip_code': 'asd12'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertFormError(response, 'form', 'zip_code', 'Zip code can only contain digits.')

    def test_new_address_form_invalid_mobile_number_non_digits(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {'mobile_number': 'asdfgtrewq'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertFormError(response, 'form', 'mobile_number', 'Mobile number can only contain digits.')

    def test_new_address_form_invalid_mobile_number_not_10_digits(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {'mobile_number': '123456789'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertFormError(response, 'form', 'mobile_number', 'Mobile number must contain 10 digits.')

    def test_new_address_invalid_form_context_contains_one_existing_addresses(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        Address.objects.create(user=self.test_user, name='John Doe', country='NZ', province='WC', zip_code='00408', city='Big City', suburb='Small suburb', street_address='50 Big Street', mobile_number='0723518979')
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('existing_addresses', response.context)
        self.assertEqual(len(response.context['existing_addresses']), 1)
        self.assertIsInstance(response.context['existing_addresses'][0], Address)

    def test_new_address_saved(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {
            'name': 'John doe',
            'country': 'NZ',
            'province': 'G',
            'zip_code': '12345',
            'city': 'Cape Town',
            'street_address': '15 Roarkus road',
            'mobile_number': '1234567890'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Address.objects.count(), 1)

    def test_new_address_related_to_user(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {
            'name': 'John doe',
            'country': 'NZ',
            'province': 'G',
            'zip_code': '12345',
            'city': 'Cape Town',
            'street_address': '15 Roarkus road',
            'mobile_number': '1234567890'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Address.objects.filter(user=self.test_user).count(), 1)

    def test_404_for_existing_address_invalid_address_id(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        Address.objects.create(user=self.test_user, name='John Doe', country='NZ', province='WC', zip_code='00408', city='Big City', suburb='Small suburb', street_address='50 Big Street', mobile_number='0723518979')
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {'addresses': 2})
        self.assertEqual(response.status_code, 404)

    def test_payment_creation_with_existing_address(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        address = Address.objects.create(user=self.test_user, name='John Doe', country='NZ', province='WC', zip_code='00408', city='Big City', suburb='Small suburb', street_address='50 Big Street', mobile_number='0723518979')
        address.save()
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {'addresses': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(Payment.objects.filter(address=address).count(), 1)
        self.assertEqual(Payment.objects.filter(order=order).count(), 1)
        self.assertEqual(Payment.objects.filter(amount=order.total_price).count(), 1)

    def test_payment_creation_with_new_address(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {
            'name': 'John doe',
            'country': 'NZ',
            'province': 'G',
            'zip_code': '12345',
            'city': 'Cape Town',
            'street_address': '15 Roarkus road',
            'mobile_number': '1234567890'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(Payment.objects.filter(address=Address.objects.all()[0]).count(), 1)
        self.assertEqual(Payment.objects.filter(order=order).count(), 1)
        self.assertEqual(Payment.objects.filter(amount=order.total_price).count(), 1)

    def test_initial_payment_data_with_existing_address(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        address = Address.objects.create(user=self.test_user, name='John Doe', country='NZ', province='WC', zip_code='00408', city='Big City', suburb='Small suburb', street_address='50 Big Street', mobile_number='0723518979')
        address.save()
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {'addresses': 1})
        self.assertEqual(response.status_code, 200)
        self.assertIn('payment_data', response.context)
        payment_data = response.context['payment_data']
        payment = Payment.objects.filter(address=address)[0]
        self.assertEqual(payment_data['merchant_id'], settings.PAYFAST_MERCHANT_ID)
        self.assertEqual(payment_data['merchant_key'], settings.PAYFAST_MERCHANT_KEY)
        self.assertEqual(payment_data['return_url'], settings.PAYFAST_RETURN_URL)
        self.assertEqual(payment_data['cancel_url'], settings.PAYFAST_CANCEL_URL)
        self.assertEqual(payment_data['notify_url'], settings.PAYFAST_NOTIFY_URL)
        self.assertEqual(payment_data['name_first'], address.name.strip())
        self.assertEqual(payment_data['cell_number'], address.mobile_number.strip())
        self.assertEqual(payment_data['m_payment_id'], payment.id)
        self.assertEqual(payment_data['amount'], payment.amount)
        self.assertEqual(payment_data['item_name'], payment.item_name)
        # self.assertEqual(payment_data['passphrase'], settings.PAYFAST_PASSPHRASE)

    def test_initial_payment_data_with_new_address(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {
            'name': 'John doe',
            'country': 'NZ',
            'province': 'G',
            'zip_code': '12345',
            'city': 'Cape Town',
            'street_address': '15 Roarkus road',
            'mobile_number': '1234567890'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('payment_data', response.context)
        payment_data = response.context['payment_data']
        address = Address.objects.get(pk=1)
        payment = Payment.objects.filter(address=address)[0]
        self.assertEqual(payment_data['merchant_id'], settings.PAYFAST_MERCHANT_ID)
        self.assertEqual(payment_data['merchant_key'], settings.PAYFAST_MERCHANT_KEY)
        self.assertEqual(payment_data['return_url'], settings.PAYFAST_RETURN_URL)
        self.assertEqual(payment_data['cancel_url'], settings.PAYFAST_CANCEL_URL)
        self.assertEqual(payment_data['notify_url'], settings.PAYFAST_NOTIFY_URL)
        self.assertEqual(payment_data['name_first'], address.name.strip())
        self.assertEqual(payment_data['cell_number'], address.mobile_number.strip())
        self.assertEqual(payment_data['m_payment_id'], payment.id)
        self.assertEqual(payment_data['amount'], payment.amount)
        self.assertEqual(payment_data['item_name'], payment.item_name)
        # self.assertEqual(payment_data['passphrase'], settings.PAYFAST_PASSPHRASE)

    def test_valid_signature_string(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {
            'name': 'John Doe',
            'country': 'NZ',
            'province': 'G',
            'zip_code': '12345',
            'city': 'Cape Town',
            'street_address': '15 Roarkus road',
            'mobile_number': '1234567890'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('payment_data', response.context)
        payment_data = response.context['payment_data']
        signature = payment_data.pop('signature')
        test_signature_string = urlencode(payment_data, quote_via=quote_plus)
        test_signature = hashlib.md5(test_signature_string.encode())
        self.assertEqual(test_signature.hexdigest(), signature)

    def test_payment_data_contains_signature_string(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {
            'name': 'John Doe',
            'country': 'NZ',
            'province': 'G',
            'zip_code': '12345',
            'city': 'Cape Town',
            'street_address': '15 Roarkus road',
            'mobile_number': '1234567890'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('payment_data', response.context)
        self.assertIn('signature', response.context['payment_data'])

    def test_context_contains_payment_data(self):
        order = Order.objects.create(user=self.test_user)
        order.save()
        OrderItem.objects.create(item=self.product_1, order=order, quantity=1)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.post(reverse('core:checkout'), {
            'name': 'John Doe',
            'country': 'NZ',
            'province': 'G',
            'zip_code': '12345',
            'city': 'Cape Town',
            'street_address': '15 Roarkus road',
            'mobile_number': '1234567890'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('payment_data', response.context)
        self.assertIn('payfast_url', response.context)
        self.assertEqual(response.context['payfast_url'], settings.PAYFAST_URL)

#TODO add logging...
# class PaymentNotifyTest(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.test_user = User.objects.create_user(email='testuser1@gmail.com', password='password123')
#         cls.product_1 = Product.objects.create(title='Product title 1', description='Product description 1', price=5.0, category='CP')
#         cls.product_1.save()
#         cls.order = Order.objects.create(user=cls.test_user)
#         cls.order.save()
#         OrderItem.objects.create(item=cls.product_1, order=cls.order, quantity=1)
#         cls.address = Address.objects.create(user=cls.test_user, name='John Doe', country='NZ', province='WC', zip_code='00408', city='Big City', suburb='Small suburb', street_address='50 Big Street', mobile_number='0723518979')
#         cls.address.save()
#         cls.payment = Payment(amount=cls.order.total_price, address=cls.address, order=cls.order)
#         cls.payment.save()
#         cls.payment_data = {
#                     'm_payment_id': cls.payment.id,
#                     'pf_payment_id': '1089250',
#                     'payment_status': 'COMPLETE',
#                     'item_name': cls.payment.item_name,
#                     'amount_gross': cls.payment.amount,
#                     'amount_fee': cls.payment.amount * 0.15,
#                     'amount_net': cls.payment.amount * 0.85,
#                     'name_first': cls.address.name.strip(), #TODO improve client side validation, and when instance is saved, strip then...?
#                     'cell_number': cls.address.mobile_number.strip(),
#                     'merchant_id': settings.PAYFAST_MERCHANT_ID,
#                     # 'email_confirmation': 1, 1=on 0=off
#                     'passphrase': settings.PAYFAST_PASSPHRASE,
#                 }

#     def test_url_accessible_by_name(self):
#         response = self.client.post(reverse('core:payment-notify'), self.payment_data)
#         self.assertEqual(response.status_code, 200)

#     def test_payment_status_unsuccessful_signature_verification_fails(self):
#         self.payment_data['signature'] = hashlib.md5('test=letsgotest'.encode()).hexdigest()
#         response = self.client.post(reverse('core:payment-notify'), self.payment_data)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(self.payment.status, 'U')

#     def test_payment_status_unsuccessful_invalid_host(self):
#         signature_string = urlencode(self.payment_data, quote_via=quote_plus)
#         self.payment_data['signature'] = hashlib.md5(signature_string.encode()).hexdigest()
#         response = self.client.post(reverse('core:payment-notify'), self.payment_data)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(self.payment.status, 'U')

#     def test_payment_status_unsuccessful_wrong_payment_amount(self):
#         signature_string = urlencode(self.payment_data, quote_via=quote_plus)
#         self.payment_data['signature'] = hashlib.md5(signature_string.encode()).hexdigest()
#         self.payment_data['amount'] = 10.0
#         response = self.client.post(reverse('core:payment-notify'), self.payment_data)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(self.payment.status, 'U')

#     def test_payment_status_unsuccessful_invalid_payfast_response(self):
#         pass

#     def test_200_header_valid_payment_notification(self):
#         signature_string = urlencode(self.payment_data, quote_via=quote_plus)
#         self.payment_data['signature'] = hashlib.md5(signature_string.encode()).hexdigest()
#         response = self.client.post(reverse('core:payment-notify'), self.payment_data)
#         self.assertEqual(response.status_code, 200)

#     def test_payment_status_successful(self):
#         signature_string = urlencode(self.payment_data, quote_via=quote_plus)
#         self.payment_data['signature'] = hashlib.md5(signature_string.encode()).hexdigest()
#         response = self.client.post(reverse('core:payment-notify'), self.payment_data)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(self.payment.status, 'S')

#     def test_order_is_no_longer_active_when_payment_is_successful(self):
#         signature_string = urlencode(self.payment_data, quote_via=quote_plus)
#         self.payment_data['signature'] = hashlib.md5(signature_string.encode()).hexdigest()
#         response = self.client.post(reverse('core:payment-notify'), self.payment_data)
#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(self.order.is_active)

#     def test_order_placement_date(self):
#         signature_string = urlencode(self.payment_data, quote_via=quote_plus)
#         self.payment_data['signature'] = hashlib.md5(signature_string.encode()).hexdigest()
#         response = self.client.post(reverse('core:payment-notify'), self.payment_data)
#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(self.order.is_active)
#         self.assertEqual(self.order.placement_date, datetime.date.today())

#     def test_order_is_active_signature_verification_fails(self):
#         self.payment_data['signature'] = hashlib.md5('test=letsgotest'.encode()).hexdigest()
#         response = self.client.post(reverse('core:payment-notify'), self.payment_data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(self.order.is_active)

#     def test_order_is_active_invalid_host(self):
#         signature_string = urlencode(self.payment_data, quote_via=quote_plus)
#         self.payment_data['signature'] = hashlib.md5(signature_string.encode()).hexdigest()
#         response = self.client.post(reverse('core:payment-notify'), self.payment_data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(self.order.is_active)

#     def test_order_is_active_wrong_payment_amount(self):
#         signature_string = urlencode(self.payment_data, quote_via=quote_plus)
#         self.payment_data['signature'] = hashlib.md5(signature_string.encode()).hexdigest()
#         self.payment_data['amount'] = 10.0
#         response = self.client.post(reverse('core:payment-notify'), self.payment_data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(self.order.is_active)

#     def test_order_is_active_invalid_payfast_response(self):
#         pass

class OrderDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='testuser1@gmail.com', password='password123')

    def test_view_url_exists(self):
        Order.objects.create(user=self.user)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get('/orders/1/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        Order.objects.create(user=self.user)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:order-detail', kwargs={'order_id': 1}))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        Order.objects.create(user=self.user)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:order-detail', kwargs={'order_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/order_detail.html')

    def test_context_with_one_product(self):
        Order.objects.create(user=self.user)
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:order-detail', kwargs={'order_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('order' in response.context)
        self.assertTrue(isinstance(response.context['order'], Order))

    def test_404_response_with_no_order(self):
        login = self.client.login(email='testuser1@gmail.com', password='password123')
        response = self.client.get(reverse('core:order-detail', kwargs={'order_id': 1}))
        self.assertEqual(response.status_code, 404)

    #404 if order exists but does not belong to user
    #redirect if not logged in

class AccountTest(TestCase):
    pass