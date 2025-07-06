from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import random
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_deposits = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        fake_number = f"080{random.randint(10000000, 99999999)}"
        Profile.objects.create(user=instance, phone=fake_number, balance=0)

class PaymentHistory(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reference = models.CharField(max_length=100, blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.status})"
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=32, unique=True)
    ordered_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    fulfilled = models.BooleanField(default=False)
    digital_product = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.title} ({self.transaction_id})"
    
    
class DigitalProduct(models.Model):
    product = models.ForeignKey(Product, related_name='digital_products', on_delete=models.CASCADE)
    code = models.TextField()  # The digital code or string
    is_assigned = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.product.title}: {self.code[:20]}{'...' if len(self.code) > 20 else ''}"