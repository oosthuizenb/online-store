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
        pass

    def test_validation_error_with_empty_username(self):
        pass

    def test_validation_error_with_empty_password(self):
        pass

    def test_correct_template_with_invalid_form(self):
        # test for message and template
        pass
    #TODO test successful/non user creation, test messages, test redirect and render

    def test_view_403_with_put_request(self):
        response = self.client.put(reverse('core:register'))
        self.assertEqual(response.status_code, 405)
