from django.shortcuts import render
from rest_framework import viewsets,permissions,generics, serializers,status,filters
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
from django_filters.rest_framework import DjangoFilterBackend
import django_filters

class AdminDashboardView(APIView):
    def get(self, request):
        if not (request.user and request.user.is_superuser):
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response({
            "message": "Welcome to the admin dashboard.",
            "endpoints": {
                "companies": "/admin/companies/",
                "customers": "/admin/customers/",
                "products": "/admin/products/",
                "orders": "/admin/orders/",
            }
        }, status=status.HTTP_200_OK)

class CustomerDashboardView(APIView):
    def get(self, request):
        if not self.request.user.is_authenticated and hasattr(self.request.user, 'customer'):
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response({
            "message": "Welcome to the Customer dashboard.",
            "endpoints": {
                "products": "/api/customer-products/",
                "cart": "/api/carts/",
                "orders": "/api/orders/",
            }
        }, status=status.HTTP_200_OK)
    
class CompanyDashboardView(APIView):
    def get(self, request):
        if  not self.request.user.is_authenticated and hasattr(self.request.user, 'company'):
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response({
            "message": "Welcome to the Company dashboard.",
            "endpoints": {
                "products": "/api/products/",
                "orders": "/api/orders/",
                "categories": "/api/categories/",
                "sizes": "/api/sizes/"
            }
        }, status=status.HTTP_200_OK)
    
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
    serializer_class = CustomerSignupSerializer
    queryset = Customer.objects.all()
    permission_classes = [IsAdminUser]

class ProductAdminViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAdminUser]

class OrderAdminViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
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
    def orders_with_items(self, request, pk=None):
        company = self.get_object()
        orders = Order.objects.filter(items__product__company=company).distinct()
        data = [
            {
                "order_id": order.id,
                "customer": order.customer.user.get_full_name(),
                "status": order.status,
                "items": [
                    {
                        "product": item.product.name,
                        "quantity": item.quantity
                    } for item in order.items.all()
                ]
            } for order in orders
        ]
        return Response(data)

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

    @action(detail=True, methods=['patch'], url_path='update-order-status')
    def update_order_status(self, request, pk=None):
        company = self.get_object()
        try:
            order = Order.objects.get(pk=request.data.get("order_id"), items__product__company=company)
        except Order.DoesNotExist:
            return Response({"error": "Order not found or not associated with this company."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in ['Pending', 'Shipped', 'Delivered', 'Cancelled']:
            return Response({"error": "Invalid status provided."}, status=status.HTTP_400_BAD_REQUEST)

        if new_status == "Shipped":
            for item in order.items.all():
                if item.product.stock < item.quantity:
                    return Response({
                        "error": f"Insufficient stock for product '{item.product.name}'."
                    }, status=status.HTTP_400_BAD_REQUEST)
                item.product.stock -= item.quantity
                item.product.save()

        order.status = new_status
        order.save()
        return Response({
            "status": "Order status updated successfully.",
            "order_id": order.id,
            "new_status": order.status
        }, status=status.HTTP_200_OK)
    
class ProductFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['category', 'price_min', 'price_max']

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'category__name']
    filterset_class = ProductFilter
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Check if the user has an associated company
            if hasattr(self.request.user, 'company'):
                return Product.objects.filter(company=self.request.user.company)
            else:
                raise PermissionDenied("You must have a company associated with your account to add products.")
        return Product.objects.none()

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to add a product.")
        
        if not hasattr(self.request.user, 'company'):
            raise PermissionDenied("You must have a company associated with your account to add products.")
        
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

class OrderViewSet(viewsets.ModelViewSet): 
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'company'):  
            return Order.objects.filter(items__product__company__user=user).distinct()
        elif hasattr(user, 'customer'): 
            return Order.objects.filter(customer__user=user).distinct()
        else:
            return Order.objects.none()

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in ['Pending', 'Shipped', 'Delivered', 'Cancelled']:
            return Response({"error": "Invalid status provided."}, status=status.HTTP_400_BAD_REQUEST)

        if order.status == 'Shipped' and new_status != 'Shipped':
            self.restore_stock(order)

        if new_status == 'Shipped':
            self.decrease_stock(order)
            notify_customer(order)

        if new_status == 'Cancelled':
            self.restore_stock(order)

        order.status = new_status
        order.save()

        return Response({
            "status": "Order status updated successfully",
            "order_id": order.id,
            "new_status": order.status
        }, status=status.HTTP_200_OK)

    def decrease_stock(self, order):
        for item in order.items.all():
            if item.product.stock < item.quantity:
                raise ValueError(f"Insufficient stock for product '{item.product.name}'")
            item.product.stock -= item.quantity
            item.product.save()

    def restore_stock(self, order):
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save()

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
        
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        customer = Customer.objects.get(user=request.user)
        cart = Cart.objects.get(customer=customer)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        payment_method = request.data.get("payment_method", "Cash on Delivery")

        order = Order.objects.create(customer=customer, payment_method="Cash on Delivery", status="Pending")
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
               
            )
            
        notify_company(order)
        cart_items.delete()

        return Response({
            "status": "Checkout successful",
            "order_id": order.id,
            "message": f"Your order has been placed with {payment_method}"
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def view_orders(self, request):
        orders_url = request.build_absolute_uri('/api/orders/') 
        return Response({
            "message": "Click the link below to view your orders.",
            "orders_url": orders_url
        })


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
            user_type = serializer.validated_data['user_type'] 
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            if user.is_superuser:
                redirect_url = '/admin/dashboard/' 
            elif user_type == 'company':  # Check if the user is a company
                redirect_url = '/company/dashboard/'
            elif user_type == 'customer':  # Check if the user is a customer
                redirect_url = '/customer/dashboard/'
            else:
                redirect_url = '/api/default/'

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