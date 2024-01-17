from django.urls import path
from core.views import CreateUserView,UserLoginView,ProductAPIView

urlpatterns = [
    
    path('public/u/create',CreateUserView.as_view(), name="Register" ),
    path('public/u/login',UserLoginView.as_view(), name="Login" ),
    path('public/product/create',ProductAPIView.as_view(), name="CreateProduct" ),
]

