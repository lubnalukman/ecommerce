
from django.contrib import admin
from .models import Company, Customer, Product, Category, Size, Order, OrderItem, Cart, CartItem

# Register each model
admin.site.register(Company)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Size)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
