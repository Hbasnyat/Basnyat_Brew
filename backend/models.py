from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.db.models.signals import pre_save
from django.dispatch import receiver
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email=email, username=username, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Flavour(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Sweetener(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Milk(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name




class Category(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    cafe_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    def __str__(self):
        return self.cafe_name

class Product(models.Model):
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    dollarprice= models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    image = models.ImageField(upload_to='product_images/')  # Added image field
    locations = models.ManyToManyField(Location, related_name='drinks')
    shortdescription = models.CharField(max_length=100,blank=True, null=True);
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='drinks',null=True)
    flavour = models.ManyToManyField(Flavour, related_name='products',blank=True)
    sweeteners = models.ManyToManyField(Sweetener, related_name='products',blank=True)
    milk = models.ManyToManyField(Milk, related_name='products',blank=True)
    def __str__(self):
        return self.name

@receiver(pre_save, sender=Product)
def convert_price_to_dollar(sender, instance, **kwargs):
    if instance.price is not None:
        dollar_price = round(Decimal(instance.price) / 130, 2)  # Convert rupees to dollars
        instance.dollarprice = dollar_price

   

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE,null=True)  # Add this field if it's missing

    def __str__(self):
        return f"Cart"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    milk = models.CharField(max_length=100, blank=True, null=True)
    sweetener = models.CharField(max_length=255, blank=True, null=True) 
    cup_size = models.CharField(max_length=255, blank=True, null=True)
    flavour = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, related_name='orders')
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    milk = models.CharField(max_length=100, blank=True, null=True)
    flavour = models.CharField(max_length=255, blank=True, null=True)
    sweetener = models.CharField(max_length=255, blank=True, null=True)
    cup_size = models.CharField(max_length=255, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created_at = models.DateTimeField(default=timezone.now)  # Add this field
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"


class Subscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed = models.BooleanField(default=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    subject = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return f"Message from {self.name}"