from django.shortcuts import render
from rest_framework import viewsets,permissions,generics, serializers,status
from .serializers import  UserSigninSerializer
from .serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import redirect, render
from django.contrib.auth import login
import requests

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

def index(request):
    return render(request,"index.html")

class UserSignupView(APIView):
    def post(self,request,*args,**kwargs):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
def signuppage(request):
    response_data = None
    try:
        response = requests.get('http://127.0.0.1:8000/api/signup/')  
        if response.status_code == 200:
            response_data = response.json()  
    except requests.exceptions.RequestException as e:
        print("Error fetching data from API:", e)
    return render(request, 'signup.html', {'response': response_data})

class UserSigninView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSigninSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('/admin/')  
                elif hasattr(user, 'company'):  
                    return redirect('http://127.0.0.1:8000/api/companies/')  
                elif hasattr(user, 'customer'):  
                    return redirect('http://127.0.0.1:8000/api/customers/')  
                    return Response({"error": "User type not identified"}, status=status.HTTP_400_BAD_REQUEST)
                
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
