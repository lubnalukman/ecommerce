from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ecomapp import views
from ecomapp.views import *
from rest_framework_simplejwt.views import(TokenObtainPairView,TokenRefreshView)

router = DefaultRouter()
router.register(r'admin/companies', views.CompanyAdminViewSet, basename='company-admin')
router.register(r'admin/customers', views.CustomerAdminViewSet, basename='customer-admin')
router.register(r'admin/products', views.ProductAdminViewSet, basename='product-admin')
router.register(r'companies', CompanyViewSet,basename='company-view')
router.register(r'customers', CustomerViewSet,basename='customer-view')
router.register(r'products', ProductViewSet,basename='product-view',)
router.register(r'customer-products', views.ProductCustomerViewSet, basename='customer-product')
router.register(r'categories', CategoryViewSet,basename='category-view')
router.register(r'sizes', SizeViewSet,basename='size-view')
router.register(r'orders', OrderViewSet,basename='order-view')
router.register(r'orderitems', OrderItemViewSet,basename='orderitem-view')
router.register(r'cart', CartViewSet,basename='cart-view')
router.register(r'cartitems', CartItemViewSet,basename='cartitem-view')
router.register(r'admin/companies', CompanyAdminViewSet, basename='admin-companies')
router.register(r'admin/customers', CustomerAdminViewSet, basename='admin-customers')
router.register(r'admin/products', ProductAdminViewSet, basename='admin-products')


urlpatterns = [
    path('', include(router.urls)),
    #path('',views.index,name='index'),
    path('customersignup/', CustomerSignupView.as_view(), name='customersignup'),
    path('companysignup/', CompanySignupView.as_view(), name='companysignup'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('api/token/',TokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('api/token/refresh',TokenRefreshView.as_view(),name='token_refresh'),
]
