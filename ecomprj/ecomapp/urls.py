from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ecomapp import views
from ecomapp.views import *

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'sizes', SizeViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'orderitems', OrderItemViewSet)
router.register(r'cart', CartViewSet)
router.register(r'cartitems', CartItemViewSet)

urlpatterns = [
    #path('', include(router.urls)),
    path('',views.index,name='index'),
    path('api/signup/', UserSignupView.as_view(), name='user-signup'),
    path('signup/', views.signuppage, name='signup-page'),
    path('api/signin/', UserSigninView.as_view(), name='user-signin'),
]
