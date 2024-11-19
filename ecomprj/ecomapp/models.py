from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='company')
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    website=models.URLField(null=True,blank=True)
    verification_status = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='customer')
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category=models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    stock_quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.company.name}"
      
class Size(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]
    product = models.ForeignKey(Product, related_name="sizes", on_delete=models.CASCADE)
    size = models.CharField(max_length=2, choices=SIZE_CHOICES)
    stock_quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.get_size_display()}"

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(max_length=50, default='Cash on Delivery')
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')],
        default='Pending'
    )

    def __str__(self):
        return f"Order {self.id} - {self.customer.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} (x{self.quantity}) in {self.order.id}"


class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')

    def __str__(self):
        return f"Cart - {self.customer.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)  

    def __str__(self):
        return f"{self.product.name} (x{self.quantity}) -Size: {self.size} in Cart - {self.cart.customer.user.username}"
