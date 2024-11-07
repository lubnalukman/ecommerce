from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

'''class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']'''

class CompanySerializer(serializers.ModelSerializer):
    #user = UserSerializer(read_only=True)
    class Meta:
        model=Company
        fields=['id','name','address','website','user','verification_status']
        read_only_fields=['id','verification_status']

class CustomerSerializer(serializers.ModelSerializer):
    #user = UserSerializer(read_only=True)
    class Meta:
        model=Customer
        fields=['id','address','phone_number','user']
        read_only_fields=['id']

class SizeSerializer(serializers.ModelSerializer):
    #size_display = serializers.CharField(source='get_size_display', read_only=True)

    class Meta:
        model = Size
        fields = ['id', 'product', 'size', 'stock_quantity']

class ProductSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    sizes = SizeSerializer(many=True, read_only=True)
    class Meta:
        model=Product
        fields=['id','company','name','description','category','price','image','stock_quantity','sizes']
        read_only_fields=['id']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','name','description']
        read_only_fields=['id']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model=OrderItem
        fields=['id','order','product','quantity']
        read_only_fields=['id']

class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model=Order
        fields=['id','customer','created_at','updated_at','status','items']
        read_only_fields=['id','created_at','updated_at']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity']
        read_only_fields = ['id']

class CartSerializer(serializers.ModelSerializer):
    customer=CustomerSerializer(read_only=True)
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)
    
    class Meta:
        model=Cart
        fields = ['id', 'customer', 'items']
        read_only_fields = ['id']


