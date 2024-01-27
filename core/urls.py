from django.urls import path
from rest_framework.routers import DefaultRouter
from core.views import CreateUserView, UserLoginView, ProductAPIView, UserProductsViewSet,ADS, Favourite,OrderView,ReviewsCreateAPIView,ShowFavourite,ShowOrder,ShowReviews, ProductSearchView, DeleteProductView,SendNotificationView, SendMsg, GoogleLoginApi
router = DefaultRouter()


urlpatterns = [
    path("public/notification", SendNotificationView.as_view(), name="Register"),
    path("public/u/create", CreateUserView.as_view(), name="Register"),
    path('public/u/login', UserLoginView.as_view(), name="Login"),
    path('google/u/auth', GoogleLoginApi.as_view(), name="google-auth"),
    path('public/product/create', ProductAPIView.as_view(), name="CreateProduct"),
    path('public/products', UserProductsViewSet.as_view(), name='user-products-del'),
    path('public/products/delete', DeleteProductView.as_view(), name='user-products'),
    path('public/products/search', ProductSearchView.as_view(), name='user-products'),
    path('public/user/profile/ad', ADS.as_view(), name="user-sp-products"),
    path('public/user/create/favourite', Favourite.as_view(), name='user-favourite-products'),
    path('public/user/create/orders', OrderView.as_view(), name='user-favourite-products'),
    path('public/user/create/reviews', ReviewsCreateAPIView.as_view(), name='user-reviews-products'),
    path('public/user/profile/favourite', ShowFavourite.as_view(), name='user-show-favourite-products'),
    path('public/user/profile/order', ShowOrder.as_view(), name='user-show-order-products'),
    path('public/user/profile/reviews', ShowReviews.as_view(), name='user-show-reviews-products'),
    path('public/u/message', SendMsg.as_view(), name='user-message'),
    # path('public/u/message/<int:id>/', MessageDetailView.as_view(), name='user-message'),
    
 
]

urlpatterns += router.urls