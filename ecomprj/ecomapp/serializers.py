from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ 'id','username', 'email']

class CompanySignupSerializer(serializers.Serializer):
    user = UserSerializer(write_only=True)
    password=serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=255)
    address = serializers.CharField()
    phone_number = serializers.CharField(max_length=20)
    website = serializers.URLField(required=False)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user_data = validated_data.pop('user')
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=validated_data.pop('password')
        )
        company = Company.objects.create(user=user, **validated_data)
        return company

class CustomerSignupSerializer(serializers.Serializer):
    user = UserSerializer(write_only=True)
    password=serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    address = serializers.CharField()
    phone_number = serializers.CharField(max_length=20)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user_data = validated_data.pop('user')
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=validated_data.pop('password')
        )
        customer = Customer.objects.create(user=user, **validated_data)
        return customer

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("User account is deactivated.")

        if hasattr(user, 'company') and user.company is not None:
            user_type = 'company'
        elif hasattr(user, 'customer') and user.customer is not None:
            user_type = 'customer'
        else:
            raise serializers.ValidationError("User profile not found.")
        
        return {
            'user': user,
            'user_type': user_type  
        }

class CompanySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model=Company
        fields='__all__'
        read_only_fields=['id']

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
    company_name = serializers.CharField(source='company.name', read_only=True)
    sizes = serializers.StringRelatedField(many=True, read_only=True) 

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'company_name','sizes','stock_quantity']

       
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
    size = SizeSerializer(read_only=True) 

    class Meta:
        model = CartItem
        fields = ['product', 'quantity', 'size'] 
                           
class CartSerializer(serializers.ModelSerializer):
    customer=CustomerSerializer(read_only=True)
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)
    
    class Meta:
        model=Cart
        fields = ['customer', 'items']
        




