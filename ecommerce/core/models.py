from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django_countries.fields import CountryField

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('CP', 'Computers'),
        ('BK', 'Book'),
        ('CG', 'Clothing'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField()
    image = models.ImageField(upload_to='products', null=True, blank=True)
    publish_date = models.DateField(auto_now_add=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("core:product-detail", kwargs={"product_id": self.pk})
    
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=6, default='123', unique=True)
    placement_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f'Order #{self.pk}'
    
    @property
    def total_price(self):
        total = 0
        for item in self.orderitem_set.all():
            total = total + item.total_price
        return total
    
class OrderItem(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f'{self.quantity} of {self.item.title}'
    
    @property
    def total_price(self):
        return self.quantity * self.item.price
    
class Address(models.Model):
    PROVINCES = [
        ('', 'Select province'),
        ('WC', 'Western Cape'),
        ('NC', 'Northern Cape'),
        ('EC', 'Eastern Cape'),
        ('FS', 'Free State'),
        ('N', 'KwaZulu-Natal'),
        ('G', 'Gauteng'),
        ('NW', 'North West'),
        ('MP', 'Mpumalanga'),
        ('LM', 'Limpopo'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    country = CountryField(blank_label='Select country')
    province = models.CharField(max_length=100, choices=PROVINCES)
    zip_code = models.CharField(max_length=5)
    city = models.CharField(max_length=40)
    suburb = models.CharField(max_length=40, blank=True, null=True)
    street_address = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=10)
    is_billing = models.BooleanField(verbose_name='Billing address', default=True)
    is_shipping = models.BooleanField(verbose_name='Shipping address', default=True)
    
    def __str__(self):
        return f'{self.name} at {self.street_address}'
    
class Payment(models.Model):
    amount = models.FloatField()
    item_name = models.CharField(max_length=20)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    successful = models.BooleanField(default=False)
    refund = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.item_name} R{self.amount}'
    
    def save(self, *args, **kwargs):
        self.item_name = f"Order #{self.order.id}"
        super().save(*args, **kwargs)