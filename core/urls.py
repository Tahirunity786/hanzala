from django.urls import path
from rest_framework.routers import DefaultRouter
from core.views import (
    CreateUserView, 
    UserLoginView, 
    ProductAPIView, 
    UserProductsViewSet,
    ADS, 
    Favourite, 
    OrderView,
    ReviewsCreateAPIView,
    ShowFavourite,
    ShowOrder,
    ShowReviews,
    ProductSearchView,
    DeleteProductView,
    SendNotificationView,
    SendMsg,
    SeeMessage,
    GoogleLoginApi,
    UserInfo
)

# Create a DefaultRouter for automatic URL routing with ViewSets
router = DefaultRouter()

# Define individual paths for your views
urlpatterns = [
    # Public notification endpoint
    path("public/notification", SendNotificationView.as_view(), name="Register"),

    # User registration endpoint
    path("public/u/create", CreateUserView.as_view(), name="Register"),

    # User login endpoint
    path('public/u/login', UserLoginView.as_view(), name="Login"),

    # Google authentication endpoint
    path('google/u/auth', GoogleLoginApi.as_view(), name="google-auth"),

    # User information save endpoint
    path("public/info/save", UserInfo.as_view(), name="Register"),

    # Product creation endpoint
    path('public/product/create', ProductAPIView.as_view(), name="CreateProduct"),

    # View for listing and deleting user products
    path('public/products', UserProductsViewSet.as_view(), name='user-products-del'),

    # Delete user product endpoint
    path('public/products/delete', DeleteProductView.as_view(), name='user-products'),

    # Search products endpoint
    path('public/products/search', ProductSearchView.as_view(), name='user-products'),

    # User ads creation endpoint
    path('public/user/profile/ad', ADS.as_view(), name="user-sp-products"),

    # User favorite products creation endpoint
    path('public/user/create/favourite', Favourite.as_view(), name='user-favourite-products'),

    # User order creation endpoint
    path('public/user/create/orders', OrderView.as_view(), name='user-favourite-products'),

    # User reviews creation endpoint
    path('public/user/create/reviews', ReviewsCreateAPIView.as_view(), name='user-reviews-products'),

    # View for showing user favorite products
    path('public/user/profile/favourite', ShowFavourite.as_view(), name='user-show-favourite-products'),

    # View for showing user orders
    path('public/user/profile/order', ShowOrder.as_view(), name='user-show-order-products'),

    # View for showing user reviews
    path('public/user/profile/reviews', ShowReviews.as_view(), name='user-show-reviews-products'),

    # User message creation endpoint
    path('public/u/message', SendMsg.as_view(), name='user-message'),

    # View for seeing user messages
    path('public/u/message/see', SeeMessage.as_view(), name='user-message'),
]

# Include the URLs generated by the DefaultRouter for ViewSets
urlpatterns += router.urls
