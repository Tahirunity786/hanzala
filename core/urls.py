from django.urls import path
from rest_framework.routers import DefaultRouter
from core.views import CreateUserView, UserLoginView, ProductAPIView, UserProductsViewSet,ADS, Favourite,OrderView,ReviewsCreateAPIView,ShowFavourite,ShowOrder,ShowReviews

router = DefaultRouter()


urlpatterns = [
    path("public/u/create", CreateUserView.as_view(), name="Register"),
    path('public/u/login', UserLoginView.as_view(), name="Login"),
    path('public/product/create', ProductAPIView.as_view(), name="CreateProduct"),
    path('public/products', UserProductsViewSet.as_view(), name='user-products'),
    path('public/user/profile/ad', ADS.as_view(), name="user-sp-products"),
    path('public/user/create/favourite', Favourite.as_view(), name='user-favourite-products'),
    path('public/user/create/orders', OrderView.as_view(), name='user-favourite-products'),
    path('public/user/create/reviews', ReviewsCreateAPIView.as_view(), name='user-reviews-products'),
    path('public/user/profile/favourite', ShowFavourite.as_view(), name='user-show-favourite-products'),
    path('public/user/profile/order', ShowOrder.as_view(), name='user-show-order-products'),
    path('public/user/profile/reviews', ShowReviews.as_view(), name='user-show-reviews-products'),
    
 
]

urlpatterns += router.urls