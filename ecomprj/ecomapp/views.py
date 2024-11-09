from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *

class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset=Company.objects.all()

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    queryset=Customer.objects.all()

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset=Product.objects.all()

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset=Category.objects.all()

class SizeViewSet(viewsets.ModelViewSet):
    serializer_class = SizeSerializer
    queryset=Size.objects.all()

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset=Order.objects.all()

class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    queryset=OrderItem.objects.all()

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    queryset=Cart.objects.all()

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    queryset=CartItem.objects.all()