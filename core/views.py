import os
from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from core.serializers import CreateUserSearializer, OrderSerializer, ProductImageSerializer, ProductSerializer, ReviewsSerializer, UserProductsSerializer, Userfavouriteproduct, DeleteProductSerializer
from core.rendenerers import UserRenderer
from random import randint
from core.tokken_agent import get_tokens_for_user
from rest_framework.permissions import IsAuthenticated, AllowAny
import uuid
from core.models import FavouritesSaved, Order, ProductImage, UserProducts
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from django.conf import settings
from collections import defaultdict
from django.db.models import Prefetch
from core.models import Reviews
from rest_framework import generics
from django.shortcuts import get_object_or_404
from firebase_admin import credentials
import firebase_admin
credential_path = os.path.join(settings.BASE_DIR, "hanzala-ab5c5-firebase-adminsdk-rg84h-7490b8f388.json")

cred = credentials.Certificate(credential_path)
firebase_admin.initialize_app(cred)


from firebase_admin import messaging
# Create your views here.
class CreateUserView(APIView):
    """
    Class-based view for creating a new user account.

    This view handles the creation of a new user account, including validation,
    saving the user instance, and generating an authentication token.

    Methods:
        - post(request): Handles the HTTP POST request for creating a new user.

    Returns:
        Response: JSON response with account details or validation errors.

    Example:
        To create a new user, send a POST request to /create_user/ with the required data.
    """
    
    # Attributes
    renderer_classes = [UserRenderer]

    def post(self, request, *args, **kwargs):
        """
        Handles the HTTP POST request for creating a new user.

        Args:
            request (rest_framework.request.Request): The HTTP request object.

        Returns:
            Response: JSON response with account details or validation errors.

        Raises:
            status.HTTP_201_CREATED: If the user account is successfully created.
            status.HTTP_406_NOT_ACCEPTABLE: If there are validation errors in the provided data.
        """
        serializer = CreateUserSearializer(data=request.data)

        if serializer.is_valid():
            account = serializer.save()
            tokken = get_tokens_for_user(account)
            
            
            response_data = {
                'response': 'Account has been created',
                'username': account.username,
                'email': account.email,
                'id': account.id,
                'token': tokken
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            error_data = serializer.errors
            return Response(error_data, status=status.HTTP_406_NOT_ACCEPTABLE)
             
class UserLoginView(APIView):
    """
    Class-based view for user authentication.

    This view handles user authentication by verifying the provided username and password
    against the user database using the Django authenticate function.

    Methods:
        - post(request): Handles the HTTP POST request for user authentication.

    Returns:
        Response: JSON response indicating the success or failure of authentication.

    Example:
        To authenticate a user, send a POST request to /user_login/ with valid credentials.
    """
    
    # Attributes
    renderer_classes = [UserRenderer]
    
    def post(self, request, *args, **kwargs):
        """
        Handles the HTTP POST request for user authentication.

        Args:
            request (rest_framework.request.Request): The HTTP request object.

        Returns:
            Response: JSON response indicating the success or failure of authentication.

        Raises:
            status.HTTP_200_OK: If authentication is successful.
            status.HTTP_401_UNAUTHORIZED: If authentication fails.
        """
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            token = get_tokens_for_user(user)
            # Authentication successful
            return Response({"success": "Logged In successfully", "token":token}, status=status.HTTP_200_OK)
        else:
            # Authentication failed
            return Response({"Error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        
        

class ProductAPIView(APIView):
    """
    API View for selling a product.

    Requires authentication.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    renderer_classes = [UserRenderer]

    def post(self, request):
        """
        Sell a product.

        Parameters:
        - request (HttpRequest): The HTTP request object containing product data.

        Returns:
        - Response: A JSON response indicating success or failure.
        """
        # Serialize product data
        serializer = ProductSerializer(data=request.data)
 
        if serializer.is_valid():
            # Create and save the product
            product = serializer.save()

            # Set the user for the product
            username = request.user
            user = User.objects.filter(username=username).first()
            if user:
                product.username = user
                product.save()
            else:
                return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

            # Process and save product images
            images = []
            for image_data in request.data.getlist('images'):
                product_image = ProductImage.objects.create(image=image_data)
                product.product_image.add(product_image)
                images.append({
                    "image_url": product_image.image.url,  # Assuming you want to include the URL
                })

            # Set product token and save
            product.product_token = uuid.uuid4()
            product.save()

            # Prepare response data
            response_data = {
                "success": "Your product was added successfully",
                "product": {
                    "product_category": product.category,
                    "product_user_image": product.user_image.url if product.user_image else '',  # Convert ImageFieldFile to URL string
                    "product_id": product.id,
                    "product_token": str(product.product_token),
                    "product_images": images,
                    "product_title": product.product_title,
                    "product_description": product.product_description,
                    "product_condition": product.condition,
                    "product_brand": product.brand,
                    "product_color": product.color,
                    "product_model": product.model,
                    "product_ram": product.ram,
                    "product_storage": product.storage,
                    "product_battery_capacity": product.battery_capacity,
                    "product_price": product.price,
                    
                }
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": f"Product not created {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

class DeleteProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = DeleteProductSerializer(data=request.data)
        if serializer.is_valid():
            product_token = serializer.validated_data.get('id')
            

            # Find the product
            product = UserProducts.objects.filter(id=product_token, username=request.user).first()

            if product:
                product.delete()
                return Response({"detail": "Product deleted successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Product not found or you don't have permission to delete it"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Invalid input data"}, status=status.HTTP_400_BAD_REQUEST)


class UserProductsViewSet(APIView):

    def get(self, request):
        try:
            # Fetch all products and product images with optimized queries
            all_products = UserProducts.objects.select_related('username').prefetch_related(
                Prefetch('product_image', queryset=ProductImage.objects.all())
            ).all()

            # Use defaultdict to simplify code
            category_mapping = defaultdict(list)

            # Loop through products and serialize data
            for product in all_products:
                serialized_product = UserProductsSerializer(product).data
                serialized_images = ProductImageSerializer(product.product_image.all(), many=True).data

                category_mapping[product.category.lower()].append({
              
                    **serialized_product,
                })

            response_data = dict(category_mapping)

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Error Details": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class ADS(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        user_id = request.user.id

        # Ensure user_id is provided in the request
        if not user_id:
            return Response({"error": "User ID is required in the request data."}, status=status.HTTP_400_BAD_REQUEST)

        # Use get_object_or_404 to handle User.DoesNotExist exception
        user = get_object_or_404(User, pk=user_id)

        # Use filter to fetch related data and then serialize
        queryset = UserProducts.objects.filter(username=user)
        serializer = UserProductsSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    
    
class Favourite(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]
    
    def post(self, request):
        # Assuming the product_id is sent in the request data
        product_id = request.data.get('product_id')
        
        try:
            # Assuming you have a method to get the current user
            user = request.user
            
            # Assuming you have a method to get the product based on the product_id
            product = UserProducts.objects.get(id=product_id)
            
            # Check if the user already has the product in favorites
            if FavouritesSaved.objects.filter(user=user, product=product).exists():
                return Response({"error": "Product is already in your favorites"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create a new FavouritesSaved instance
            favourite = FavouritesSaved.objects.create(user=user, product=product)
            
            # You might want to serialize the created instance if needed
            serializer = Userfavouriteproduct(instance=favourite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except UserProducts.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)



class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request):
        # Assuming the product_id and purchased_quantity are sent in the request data
        product_id = request.data.get('product_id')
        purchased_quantity = request.data.get('purchased_quantity')

        try:
            user = request.user
            product = UserProducts.objects.get(id=product_id)

            # Create a new Order instance
            order = Order.objects.create(user=user, product=product, purchased_quantity=purchased_quantity)
            order.activate_order = "active order"
            # You might want to serialize the created instance if needed
            serializer = OrderSerializer(instance=order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except UserProducts.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)


class ReviewsCreateAPIView(generics.CreateAPIView):
    serializer_class = ReviewsSerializer

    def create(self, request, *args, **kwargs):
        # Extract data from the request
        reviews_giver = request.user  # Assuming you have authentication set up
        product_id = request.data.get('product_id')

        try:
            review_at_product = UserProducts.objects.get(id=product_id)
        except UserProducts.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create a mutable copy of request.data
        mutable_data = request.data.copy()

        # Add reviews_giver and review_at_product to the mutable data
        mutable_data['reviews_giver'] = reviews_giver.id
        mutable_data['review_at_product'] = review_at_product.id

        # Create the review instance
        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
class ShowFavourite(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        user_id = request.user.id

        # Ensure user_id is provided in the request
        if not user_id:
            return Response({"error": "User ID is required in the request data."}, status=status.HTTP_400_BAD_REQUEST)

        # Use get_object_or_404 to handle User.DoesNotExist exception
        user = get_object_or_404(User, pk=user_id)

        # Use filter to fetch related data and then serialize
        queryset = Favourite.objects.filter(user=user)
        serializer = Userfavouriteproduct(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ShowOrder(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        user_id = request.user.id

        # Ensure user_id is provided in the request
        if not user_id:
            return Response({"error": "User ID is required in the request data."}, status=status.HTTP_400_BAD_REQUEST)

        # Use get_object_or_404 to handle User.DoesNotExist exception
        user = get_object_or_404(User, pk=user_id)

        # Use filter to fetch related data and then serialize
        queryset = Order.objects.filter(user=user)
        serializer = OrderSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
class ShowReviews(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        user_id = request.user.id

        # Ensure user_id is provided in the request
        if not user_id:
            return Response({"error": "User ID is required in the request data."}, status=status.HTTP_400_BAD_REQUEST)

        # Use get_object_or_404 to handle User.DoesNotExist exception
        user = get_object_or_404(User, pk=user_id)

        # Use filter to fetch related data and then serialize
        queryset = Reviews.objects.filter(reviews_giver=user)
        serializer = ReviewsSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
class ProductSearchView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            brand_name = request.data.get('brand', None)
            product_title = request.data.get('title', None)
           

            # Check if either brand_name or product_title is provided
            if brand_name is None and product_title is None:
                return Response({"Error": "At least one query (brand or title) should be provided"}, status=status.HTTP_400_BAD_REQUEST)

            queryset = UserProducts.objects.all()

            if brand_name:
                queryset = queryset.filter(brand__icontains=brand_name)

            if product_title:
                max_title_length = 200  # Set your maximum title length here
                if len(product_title) > max_title_length:
                    raise ValueError("Product title is too long.")
                queryset = queryset.filter(product_title__icontains=product_title)

            # Check if queryset is empty after filtering
            if not queryset.exists():
                return Response({"Error": "No matching products found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = UserProductsSerializer(queryset, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except ValueError as ve:
            return Response({"detail": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "An error occurred while processing your request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SendNotificationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        title = request.data.get('title')
        body = request.data.get('body')

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )
        messaging.send(message)

        return Response({'message': 'Notification sent successfully'}, status=status.HTTP_200_OK)
    

