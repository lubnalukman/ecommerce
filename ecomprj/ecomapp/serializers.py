from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    is_seller = serializers.ChoiceField(choices=[('buy', 'Buy'), ('sell', 'Sell')], write_only=True, required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'is_seller']
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data
    def create(self, validated_data):
        validated_data.pop('confirm_password')    
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class UserSigninSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("User account is inactive.")
        data['user'] = user
        return data

class CompanySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model=Company
        fields='__all__'
        read_only_fields=['id','verification_status']

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model=Customer
        fields='__all__'
        read_only_fields=['id']

class SizeSerializer(serializers.ModelSerializer):
    size_display = serializers.CharField(source='get_size_display', read_only=True)

    class Meta:
        model = Size
        fields ='__all__' 

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields='__all__'
     

class ProductSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    sizes = SizeSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    class Meta:
        model=Product
        fields='__all__'
       
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model=OrderItem
        fields='__all__'
      
class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model=Order
        fields='__all__'
        read_only_fields=['id','created_at','updated_at']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ['id']
                           
class CartSerializer(serializers.ModelSerializer):
    customer=CustomerSerializer(read_only=True)
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)
    
    class Meta:
        model=Cart
        fields = '__all__'
        read_only_fields = ['id']




