from django.shortcuts import render
from rest_framework import viewsets,permissions,generics, serializers
from .serializers import  UserSigninSerializer
from .serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import redirect, render


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



class UserSigninView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSigninSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            if user.is_superuser:
                return redirect('/admin/home/')  # Redirect to admin page
            elif user.userprofile.user_type == 'seller':
                return redirect('/seller/home/')  # Redirect to seller home
            else:
                return redirect('/customer/home/')  # Redirect to customer home

        return render(request, 'signin.html', {'errors': serializer.errors})
