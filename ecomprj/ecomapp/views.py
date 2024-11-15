from django.shortcuts import render
from rest_framework import viewsets,permissions,generics, serializers,status
from .serializers import  LoginSerializer
from .serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import redirect, render
from django.contrib.auth import login
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Company, Category, Product, Size, Order, OrderItem
from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class CompanyAdminViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def verify_company(self, request, pk=None):
        company = self.get_object()
        company.verification_status = True
        company.save()
        return Response({"status": "Company verified successfully"})

class CustomerAdminViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    permission_classes = [IsAdminUser]

class ProductAdminViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAdminUser]

class CompanyViewSet(viewsets.ModelViewSet):  
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        company = self.get_object()
        orders = Order.objects.filter(items__product__company=company).distinct()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def order_items(self, request, pk=None):
        company = self.get_object()
        order_items = OrderItem.objects.filter(product__company=company)
        serializer = OrderItemSerializer(order_items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def customer_details(self, request, pk=None):
        company = self.get_object()
        orders = Order.objects.filter(items__product__company=company).distinct()
        customer_details = [
            {
                'name': order.customer.user.get_full_name(),
                'address': order.customer.address,
                'phone_number': order.customer.phone_number,
            } 
            for order in orders
        ]
        return Response(customer_details)

    @action(detail=True, methods=['patch'], url_path='update-shipping-status')
    def update_shipping_status(self, request, pk=None):
        company = self.get_object()
        order = get_object_or_404(Order, pk=request.data.get("order_id"))
        if not any(item.product.company == company for item in order.items.all()):
            return Response({"detail": "You can only update orders for products from your company."},
                            status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get("status")
        if new_status not in ['Pending', 'Shipped', 'Delivered', 'Cancelled']:
            return Response(
                {"detail": "Invalid status provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        return Response({"status": order.status})


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def get_queryset(self):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'company'):
            return Product.objects.filter(company__user=self.request.user)
        return Product.objects.none()

    def perform_create(self, serializer):
        company = self.request.user.company
        if not company.verification_status:
            raise PermissionDenied("Your account is not yet verified by the admin.")
        serializer.save(company=company)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    def get_queryset(self):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'company'):
            return Category.objects.filter(product__company__user=self.request.user)
        return Category.objects.none()
    

class SizeViewSet(viewsets.ModelViewSet):
    serializer_class = SizeSerializer
    queryset = Size.objects.all()
    def get_queryset(self):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'company'):
            return Size.objects.filter(product__company__user=self.request.user)
        return Size.objects.none()

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'company'):
            return Order.objects.filter(items__product__company__user=self.request.user).distinct()
        return Order.objects.none()
    
class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()

    def get_queryset(self):
       
        if self.request.user.is_authenticated and hasattr(self.request.user, 'company'):
            return OrderItem.objects.filter(product__company__user=self.request.user)
        return OrderItem.objects.none()

    @action(detail=True, methods=['get'], url_path='order-details')
    def order_details(self, request, pk=None):
        order_item = self.get_object()
        order = order_item.order
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='update-quantity')
    def update_quantity(self, request, pk=None):
        order_item = self.get_object()
        new_quantity = request.data.get("quantity")
        if new_quantity and isinstance(new_quantity, int) and new_quantity > 0:
            order_item.quantity = new_quantity
            order_item.save()
            return Response({"quantity": order_item.quantity})
        return Response({"detail": "Invalid quantity provided"}, status=status.HTTP_400_BAD_REQUEST)

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        serializer = self.get_serializer(customer)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        serializer = self.get_serializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'])
    def delete_account(self, request):
        customer = Customer.objects.get(user=request.user)
        user = customer.user
        user.delete()  
        return Response({"status": "Account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class ProductCustomerViewSet(viewsets.ReadOnlyModelViewSet): 
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  

    @action(detail=True, methods=['post'], url_path='add-to-cart')
    def add_to_cart(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        customer = request.user.customer  
        cart, created = Cart.objects.get_or_create(customer=customer)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
        else:
            cart_item.quantity = 1
            cart_item.save()    
        return Response({
            "status": "Product added to cart",
            "product": product.name,
            "quantity": cart_item.quantity
        }, status=status.HTTP_200_OK)

class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        customer = Customer.objects.get(user=request.user)
        cart, created = Cart.objects.get_or_create(customer=customer)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_product(self, request):
        customer = Customer.objects.get(user=request.user)
        cart, created = Cart.objects.get_or_create(customer=customer)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        size_id = request.data.get('size_id')  

        try:
            product = Product.objects.get(id=product_id)
            size = Size.objects.get(id=size_id)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            cart_item.quantity += quantity
            cart_item.save()
            return Response({"status": "Product added to cart"}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Size.DoesNotExist:
            return Response({"error": "Size not found"}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=['post'])
    def remove_product(self, request):
        customer = Customer.objects.get(user=request.user)
        cart = Cart.objects.get(customer=customer)
        product_id = request.data.get('product_id')

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            return Response({"status": "Product removed from cart"}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({"error": "Product not in cart"}, status=status.HTTP_404_NOT_FOUND)

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer = Customer.objects.get(user=self.request.user)
        cart = Cart.objects.get(customer=customer)
        return CartItem.objects.filter(cart=cart)

    def update(self, request, *args, **kwargs):
        cart_item = self.get_object()
        new_quantity = request.data.get("quantity", 1)
        cart_item.quantity = new_quantity
        cart_item.save()
        return Response({"status": "Cart item quantity updated", "quantity": cart_item.quantity})

#def index(request):
    #return render(request,"index.html")

class CompanySignupView(APIView):
    permission_classes = [AllowAny]  
    def post(self,request,*args,**kwargs):
        serializer = CompanySignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Company registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomerSignupView(APIView):
    permission_classes = [AllowAny]  
    def post(self,request,*args,**kwargs):
        serializer = CustomerSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Customer registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]  
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate JWT tokens for the authenticated user
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Determine the user type and redirect path
            if hasattr(user, 'company'):
                redirect_url = '/api/companies/'
            elif hasattr(user, 'customer'):
                redirect_url = '/api/customers/'
            else:
                redirect_url = '/admin/'

            return Response({
                "message": "Login successful",
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "access_token": access_token,
                "refresh_token": str(refresh),
                "redirect_url": redirect_url
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
