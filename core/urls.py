from django.urls import path
from rest_framework.routers import DefaultRouter
from core.views import CreateUserView, UserLoginView, ProductAPIView, UserProductsViewSet

router = DefaultRouter()
router.register(r'public/products', UserProductsViewSet, basename='user-products')

urlpatterns = [
    path('public/u/create', CreateUserView.as_view(), name="Register"),
    path('public/u/login', UserLoginView.as_view(), name="Login"),
    path('public/product/create', ProductAPIView.as_view(), name="CreateProduct"),
]

urlpatterns += router.urls