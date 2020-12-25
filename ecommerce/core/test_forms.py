from django.contrib.auth.models import User
from django.test import TestCase
from .forms import RegisterForm, CustomAuthenticationForm, AddressForm

class RegisterFormTest(TestCase):
    def test_email_widget_placeholder(self):
        form = RegisterForm()
        expected_placeholder = 'Email address'
        self.assertEqual(form.fields['email'].widget.attrs['placeholder'], expected_placeholder)
        
    def test_password_widget_placeholder(self):
        form = RegisterForm()
        expected_placeholder = 'Password'
        self.assertEqual(form.fields['password'].widget.attrs['placeholder'], expected_placeholder)
        
    def test_password_confirm_widget_placeholder(self):
        form = RegisterForm()
        expected_placeholder = 'Confirm password'
        self.assertEqual(form.fields['password_confirm'].widget.attrs['placeholder'], expected_placeholder)
        
    def test_unique_username_is_valid(self):
        form = RegisterForm(data={
            'email': 'test@gmail.com',
            'password': 'a_password',
            'password_confirm': 'a_password',
        })
        self.assertTrue(form.is_valid())
    
    def test_non_unique_username_is_invalid(self):
        user = User.objects.create_user(username='test@gmail.com', password='pass123')
        user.save()
        form = RegisterForm(data={
            'email': 'test@gmail.com',
            'password': 'a_password',
            'password_confirm': 'a_password',
        })
        self.assertFalse(form.is_valid())
    
    def test_password_matches_is_valid(self):
        form = RegisterForm(data={
            'email': 'test@gmail.com',
            'password': '123',
            'password_confirm': '123',
        })
        self.assertTrue(form.is_valid())
    
    def test_password_non_match_is_invalid(self):
        form = RegisterForm(data={
            'email': 'test@gmail.com',
            'password': '1234',
            'password_confirm': '123',
        })
        self.assertFalse(form.is_valid())
        
class CustomAuthenticationFormTest(TestCase):
    def test_username_widget_placeholder(self):
        form = CustomAuthenticationForm()
        expected_placeholder = 'Username'
        self.assertEqual(form.fields['username'].widget.attrs['placeholder'], expected_placeholder)
        
    def test_password_widget_placeholder(self):
        form = CustomAuthenticationForm()
        expected_placeholder = 'Password'
        self.assertEqual(form.fields['password'].widget.attrs['placeholder'], expected_placeholder)

class AddressFormTest(TestCase):
    def test_name_widget_placeholder(self):
        form = AddressForm()
        expected_placeholder = 'Recipient Name'
        self.assertEqual(form.fields['name'].widget.attrs['placeholder'], expected_placeholder)
        
    def test_zip_code_widget_placeholder(self):
        form = AddressForm()
        expected_placeholder = 'Zip Code'
        self.assertEqual(form.fields['zip_code'].widget.attrs['placeholder'], expected_placeholder)
        
    def test_city_widget_placeholder(self):
        form = AddressForm()
        expected_placeholder = 'City/Town'
        self.assertEqual(form.fields['city'].widget.attrs['placeholder'], expected_placeholder)
        
    def test_suburb_widget_placeholder(self):
        form = AddressForm()
        expected_placeholder = 'Suburb'
        self.assertEqual(form.fields['suburb'].widget.attrs['placeholder'], expected_placeholder)
        
    def test_street_address_widget_placeholder(self):
        form = AddressForm()
        expected_placeholder = 'Street Address'
        self.assertEqual(form.fields['street_address'].widget.attrs['placeholder'], expected_placeholder)
        
    def test_mobile_number_widget_placeholder(self):
        form = AddressForm()
        expected_placeholder = 'Mobile Number'
        self.assertEqual(form.fields['mobile_number'].widget.attrs['placeholder'], expected_placeholder)
        
    def test_creation_without_user_is_valid(self):
        form = AddressForm(data={
            'name': 'John Doe',
            'country': 'NZ',
            'province': 'WC',
            'zip_code': '00408',
            'city': 'Big City',
            'suburb': 'Small suburb',
            'street_address': '50 Big Street',
            'mobile_number': '0723518979'
        })
        self.assertTrue(form.is_valid())
    
    def test_zip_code_with_digits_only_is_valid(self):
        form = AddressForm(data={
            'name': 'John Doe',
            'country': 'NZ',
            'province': 'WC',
            'zip_code': '7125',
            'city': 'Big City',
            'suburb': 'Small suburb',
            'street_address': '50 Big Street',
            'mobile_number': '0723518979'
        })
        self.assertTrue(form.is_valid())
        
    def test_zip_code_with_non_digits_is_invalid(self):
        form = AddressForm(data={
            'name': 'John Doe',
            'country': 'NZ',
            'province': 'WC',
            'zip_code': 'SSW25',
            'city': 'Big City',
            'suburb': 'Small suburb',
            'street_address': '50 Big Street',
            'mobile_number': '0723518979'
        })
        self.assertFalse(form.is_valid())
        
    def test_mobile_number_with_digits_only_is_valid(self):
        form = AddressForm(data={
            'name': 'John Doe',
            'country': 'NZ',
            'province': 'WC',
            'zip_code': '7125',
            'city': 'Big City',
            'suburb': 'Small suburb',
            'street_address': '50 Big Street',
            'mobile_number': '0723518979'
        })
        self.assertTrue(form.is_valid())
        
    def test_mobile_number_with_non_digits_is_invalid(self):
        form = AddressForm(data={
            'name': 'John Doe',
            'country': 'NZ',
            'province': 'WC',
            'zip_code': '7125',
            'city': 'Big City',
            'suburb': 'Small suburb',
            'street_address': '50 Big Street',
            'mobile_number': '072as18g79'
        })
        self.assertFalse(form.is_valid())
        
    def test_mobile_number_with_10_digits_is_valid(self):
        form = AddressForm(data={
            'name': 'John Doe',
            'country': 'NZ',
            'province': 'WC',
            'zip_code': '7125',
            'city': 'Big City',
            'suburb': 'Small suburb',
            'street_address': '50 Big Street',
            'mobile_number': '0723518979'
        })
        self.assertTrue(form.is_valid())
        
    def test_mobile_number_with_9_digits_is_invalid(self):
        form = AddressForm(data={
            'name': 'John Doe',
            'country': 'NZ',
            'province': 'WC',
            'zip_code': '7125',
            'city': 'Big City',
            'suburb': 'Small suburb',
            'street_address': '50 Big Street',
            'mobile_number': '072572331'
        })
        self.assertFalse(form.is_valid())
        
    def test_mobile_number_with_11_digits_is_invalid(self):
        form = AddressForm(data={
            'name': 'John Doe',
            'country': 'NZ',
            'province': 'WC',
            'zip_code': '7125',
            'city': 'Big City',
            'suburb': 'Small suburb',
            'street_address': '50 Big Street',
            'mobile_number': '07257233101'
        })
        self.assertFalse(form.is_valid())
        
# TODO add tests for field labels

    
    # def test_rating_min_value(self):
    #     min_value = self.review._meta.get_field('rating').min_value
    #     self.assertEqual(min_value, 1)

    # def test_rating_max_value(self):
    #     max_value = self.review._meta.get_field('rating').max_value
    #     self.assertEqual(max_value, 5)