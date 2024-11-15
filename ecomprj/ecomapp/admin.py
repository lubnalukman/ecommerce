
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

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'phone_number', 'website', 'verification_status')
    list_filter = ('verification_status',)
    search_fields = ('name', 'user__username')

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'category', 'price', 'stock_quantity')
    list_filter = ('company', 'category')
    search_fields = ('name', 'company__name', 'category__name')

class SizeAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'stock_quantity')
    list_filter = ('size',)
    search_fields = ('product__name',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__user__username',)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    search_fields = ('order__id', 'product__name')

class CartAdmin(admin.ModelAdmin):
    list_display = ('customer',)
    search_fields = ('customer__user__username',)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ('cart__customer__user__username', 'product__name')
