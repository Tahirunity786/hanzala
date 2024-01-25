from django.urls import path
from rest_framework.routers import DefaultRouter
from core.views import CreateUserView, UserLoginView, ProductAPIView, UserProductsViewSet,ADS, Favourite,OrderView

router = DefaultRouter()


urlpatterns = [
    path("public/u/create", CreateUserView.as_view(), name="Register"),
    path('public/u/login', UserLoginView.as_view(), name="Login"),
    path('public/product/create', ProductAPIView.as_view(), name="CreateProduct"),
    path('public/products', UserProductsViewSet.as_view(), name='user-products'),
    path('public/user/profile/ad', ADS.as_view(), name="user-sp-products"),
    path('public/user/profile/favourite', Favourite.as_view(), name='user-favourite-products'),
    path('public/user/profile/orders', OrderView.as_view(), name='user-favourite-products'),
    
 
]

urlpatterns += router.urls