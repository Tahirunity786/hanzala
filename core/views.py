import os
import random
import string
from urllib.parse import urlparse
from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from core.serializers import CreateUserSearializer, MessageSerializer, OrderSerializer, ProductImageSerializer, ProductSerializer, ReviewsSerializer, UserProductsSerializer, Userfavouriteproduct, DeleteProductSerializer, Seemessagesearializer, notificationsearializer, UserUpdatepasswordSerializer, UserProfileSerializer, OrderUpdateSerializer
from coreadmin.serializers import UserSerializer
from core.rendenerers import UserRenderer
from random import randint
from core.tokken_agent import get_tokens_for_user
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
import uuid
from core.models import FavouritesSaved, Message, Order, ProductImage, UserProducts
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from collections import defaultdict
from django.db.models import Prefetch
from core.models import Reviews
from rest_framework import generics
from django.shortcuts import get_object_or_404
from core.notification import send_message
from django.db.models import Q
from fcm_django.models import FCMDevice
from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token
import requests as efwe
from django.db.models import Max
from coreadmin.models import PaymentModifier

User = get_user_model()

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
    permission_classes = [AllowAny]
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

        if user and not user.is_blocked:
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
        serializer = ProductSerializer(data=request.data)

        username = request.user.id
        user = User.objects.get(id=username)
        
        # Serialize product data
        if  not user.is_blocked:
            if serializer.is_valid():
                # Create and save the product
                product = serializer.save()

                # Set the user for the product
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
                user.is_seller=True
                user.save()
                product.product_token = uuid.uuid4()
                product.save()
                
                # Prepare response data
                response_data = {
                    "success": "Your product was added successfully",
                    "product": {
                        "product_seller_id": product.username.id,  # Include user ID here
                        "product_seller_image": user.profile.url if user.profile else None,
                        "product_category": product.category,
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
                        "product_notification": product.notification_token,

                    }
                }

                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": f"Product not created {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error":"Your are blocked by Admin, So cannot able to buy and sell a product"}, status=status.HTTP_401_UNAUTHORIZED)


class DeleteProductView(APIView):
    """
    API endpoint for deleting a user's product.

    Requires authentication.

    Request Format:
    {
        "id": "product_token"
    }

    Response:
    - 200 OK: Product deleted successfully
    - 404 Not Found: Product not found or user doesn't have permission to delete it
    - 400 Bad Request: Invalid input data
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to delete a user's product.

        Parameters:
        - request: The HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - Response: A JSON response indicating the result of the operation.
        """
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
    """
    API endpoint for retrieving user products grouped by category.

    This endpoint fetches all products along with their images and categorizes them by the product category.
    """

    def get(self, request):
        try:
            # Fetch all products and product images with optimized queries
            all_products = UserProducts.objects.select_related('username').prefetch_related(
                Prefetch('product_image', queryset=ProductImage.objects.all())
            ).all()

            # Fetch the first PaymentModifier record (you may need to adjust this query based on your requirements)
            payment_modifier = PaymentModifier.objects.first()

            # Use defaultdict to simplify code
            category_mapping = defaultdict(list)

            # Loop through products and serialize data
            for product in all_products:
                # Serialize product data
                serialized_product = UserProductsSerializer(product).data

                # Append 'username' and 'user_id' to the serialized product data
                serialized_product['username'] = product.username.username if product.username else None
                serialized_product['user_id'] = product.username.id if product.username else None

                # Include user image in serialized product data
                serialized_product['user_image'] = product.username.profile.url if product.username and product.username.profile else None

                # Serialize product images data
                serialized_images = ProductImageSerializer(product.product_image.all(), many=True).data

                # Append serialized product data to the corresponding category
                category_mapping[product.category.lower()].append({
                    **serialized_product,
                    'payment_modifier': {
                        'protection_fee': payment_modifier.protection_fee,
                        'delivery_fee': payment_modifier.delivery_fee,
                    }
                })

            # Create a dictionary to hold the response data
            response_data = dict(category_mapping)

            # Return the categorized product data as a JSON response
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Return an error response if an exception occurs
            return Response({"Error Details": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ADS(APIView):
    """
    API endpoint for retrieving products associated with the authenticated user.

    Method: GET
    Permission: IsAuthenticated (User must be logged in to access this endpoint)
    Renderer: UserRenderer (Custom renderer for user-specific responses)
    """

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        """
        Handle GET request to retrieve products associated with the authenticated user.

        :param request: Django request object
        :return: Response containing serialized user products data
        """
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
    """
    API endpoint for managing user favorites.

    Permissions:
        - User must be authenticated to access this endpoint.

    Request:
        - POST: Add a product to the user's favorites.

    Response:
        - 201 Created: Product successfully added to favorites.
        - 400 Bad Request: Product is already in user's favorites.
        - 404 Not Found: Product not found.
    """

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request):
        """
        Add a product to the user's favorites.

        Args:
            request: Django Rest Framework request object.

        Returns:
            Response: JSON response containing the serialized favorite product or an error message.

        Raises:
            UserProducts.DoesNotExist: If the specified product does not exist.
        """

        # Assuming the product_id is sent in the request data
        product_id = request.data.get('product_id')

        try:
            # Assuming you have a method to get the current user
            user = request.user

            # Assuming you have a method to get the product based on the product_id
            product = UserProducts.objects.get(id=product_id)

            # Check if the user already has the product in favorites
            if FavouritesSaved.objects.filter(user=user, product=product).exists():
                return Response(
                    {"error": "Product is already in your favorites"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create a new FavouritesSaved instance
            favourite = FavouritesSaved.objects.create(user=user, product=product)

            # You might want to serialize the created instance if needed
            serializer = Userfavouriteproduct(instance=favourite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except UserProducts.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)



class OrderView(APIView):
    """
    API endpoint for creating orders.

    Requires authentication.

    Supports HTTP POST request to create a new order.
    """

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request):
        """
        Create a new order.

        Parameters:
        - product_id (int): The ID of the product to be ordered.
        - purchased_quantity (int): The quantity of the product to be purchased.

        Returns:
        - Response: Serialized order data if successful, error response otherwise.
        """

        # Extract data from the request
        product_id = request.data.get('product_id')
      
        payment_method = request.data.get('payment_method')
        # For notification
        device_token = request.data.get('device_token')
        title = "Order Confirmed. "
        body = "Thank you for your order. It will be delivered within 7 working days."

        try:
            # Get the authenticated user
            user = request.user

            # Retrieve the product based on the provided product_id
            product = UserProducts.objects.get(id=product_id)

            # Create a new Order instance
            order = Order.objects.create(user=user, product=product, payment_method=payment_method)
            order.activate_order = "active order"

            # Serialize the created order instance
            serializer = OrderSerializer(instance=order)
            # Send a notification
            send_message(device_token, body, title)
            # Return a successful response with serialized order data
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except UserProducts.DoesNotExist:
            # Return a 404 error response if the specified product does not exist
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)



class ReviewsCreateAPIView(generics.CreateAPIView):
    """
    API endpoint for creating product reviews.

    This endpoint allows an authenticated user to submit a review for a specific product.

    Request Payload:
        - product_id: The ID of the product for which the review is being submitted.

    Response:
        - Returns the serialized data of the created review.

    Note:
        - Assumes user authentication is set up.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewsSerializer

    def create(self, request, *args, **kwargs):
        # Extract data from the request
        reviews_giver = request.user  # Assuming you have authentication set up
        product_id = request.data.get('product_id')

        try:
            review_at_product = UserProducts.objects.get(id=product_id)
        except UserProducts.DoesNotExist:
            return Response({'Error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

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
    """
    API endpoint to retrieve a user's favorite products.

    Requires authentication. Returns a list of favorite products associated with the user.

    Endpoint: GET /api/show-favorite/
    """

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        """
        Handles GET requests to retrieve the user's favorite products.

        :param request: The HTTP GET request.
        :return: Response with a list of serialized favorite products.
        """

        # Extract user ID from the authenticated user
        user_id = request.user.id

        # Ensure user_id is provided in the request
        if not user_id:
            return Response({"error": "User ID is required in the request data."}, status=status.HTTP_400_BAD_REQUEST)

        # Use get_object_or_404 to handle User.DoesNotExist exception
        user = get_object_or_404(User, pk=user_id)

        # Use filter to fetch related data and then serialize
        queryset = FavouritesSaved.objects.filter(user=user)
        serializer = Userfavouriteproduct(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
class ShowOrder(APIView):
    """
    API endpoint to retrieve orders for the authenticated user.

    Requires authentication using Token or other authentication methods.
    
    Returns a JSON array of orders associated with the authenticated user.

    Response Format:
    [
        {
            "id": 1,
            "product_name": "Product A",
            "quantity": 2,
            "total_price": 20.0,
            "created_at": "2024-01-27T12:00:00Z",
            "updated_at": "2024-01-27T12:30:00Z"
        },
        {
            "id": 2,
            "product_name": "Product B",
            "quantity": 1,
            "total_price": 15.0,
            "created_at": "2024-01-27T14:00:00Z",
            "updated_at": "2024-01-27T14:15:00Z"
        },
        ...
    ]
    """

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]  # Make sure to replace with your actual renderer

    def get(self, request):
        """
        Handle GET requests to retrieve orders for the authenticated user.

        Args:
        - request: The HTTP request object.

        Returns:
        - Response: A JSON response containing a list of serialized orders.
        """
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
    """
    API endpoint to retrieve reviews given by the authenticated user.

    Requires authentication.

    
    """

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]  # Replace with your renderer, if needed

    def get(self, request):
        """
        Handle GET request to retrieve reviews given by the authenticated user.

        Returns:
            Response: Serialized reviews data in JSON format.
        """

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
    """
    API endpoint for searching user products based on brand or title.

    Permissions:
        - AllowAny: No authentication required for searching.

    Methods:
        - POST: Search for products based on brand or title.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for searching user products.

        Parameters:
            - request: The incoming HTTP request.
            - args: Additional positional arguments.
            - kwargs: Additional keyword arguments.

        Returns:
            - Response: JSON response containing the search results or error details.
        """
        try:
            # Retrieve brand_name and product_title from request data
            brand_name = request.data.get('brand', None)
            product_title = request.data.get('title', None)

            # Check if either brand_name or product_title is provided
            if brand_name is None and product_title is None:
                return Response({"Error": "At least one query (brand or title) should be provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Initialize the queryset with all user products
            queryset = UserProducts.objects.all()

            # Apply filters based on brand_name
            if brand_name:
                queryset = queryset.filter(brand__icontains=brand_name)

            # Apply filters based on product_title
            if product_title:
                # Set the maximum allowed title length
                max_title_length = 200  

                # Check if product_title exceeds the maximum allowed length
                if len(product_title) > max_title_length:
                    raise ValueError("Product title is too long.")

                # Apply filter for product_title
                queryset = queryset.filter(product_title__icontains=product_title)

            # Check if queryset is empty after filtering
            if not queryset.exists():
                return Response({"Error": "No matching products found"}, status=status.HTTP_404_NOT_FOUND)

            # Serialize the queryset results
            serializer = UserProductsSerializer(queryset, many=True)

            # Return the serialized data in the response
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except ValueError as ve:
            # Handle ValueError exceptions (e.g., product_title too long)
            return Response({"detail": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Handle other exceptions (e.g., generic exceptions)
            return Response({"detail": "An error occurred while processing your request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SendNotificationView(APIView):
    """
    API endpoint for sending push notifications to a specific device.

    Parameters:
    - `token` (str): The FCM registration token of the target device.
    - `title` (str): The title of the notification.
    - `body` (str): The body/content of the notification.

    Note: This endpoint does not require authentication (AllowAny permission).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = notificationsearializer
    
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            data_dict = serializer.validated_data

            # Check if the device with the given registration_id already exists
            existing_device = FCMDevice.objects.filter(registration_id=data_dict.get('token')).first()

            if existing_device:
                # If the device already exists, update its details
                existing_device.name = "android"
                existing_device.user = request.user
                existing_device.type = "android"
                existing_device.save()
            else:
                # If the device doesn't exist, create a new one
                new_device = FCMDevice(
                    name="android",
                    registration_id=data_dict.get('token'),
                    device_id=str(uuid.uuid4()),
                    user=request.user,
                    type="android"
                )
                new_device.save()

            is_sent = send_message(data_dict.get('token'), data_dict.get('title'), data_dict.get('body'))

            if is_sent:
                return Response({'message': 'Notification sent successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Notification not sent successfully'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendMsg(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Assuming the request data contains 'receiver_id' and 'content'
        receiver_id = request.data.get('receiver_id')
        content = request.data.get('content')
        order_id = request.data.get('order_id')

        # Get the sender (current user) from the request
        sender = request.user

        # Check if the receiver exists
        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({"error": "Receiver does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        sender_user = User.objects.get(id=sender.id)
        if not sender_user.is_blocked and not receiver.is_blocked:
            # Create the message
            message = Message.objects.create(sender=sender, receiver=receiver, content=content, order_id=order_id)

            # You might want to add additional logic here, such as updating unread counts, notifications, etc.

            # Serialize the created message
            serializer = MessageSerializer(message)

            # Return the serialized data in the response
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif sender_user.is_blocked:
            return Response({"error": "You are blocked by an admin, you can't send a message"}, status=status.HTTP_403_FORBIDDEN)
        elif receiver.is_blocked:
            return Response({"error": "Receiver is blocked, your message cannot be sent"}, status=status.HTTP_403_FORBIDDEN)


class SeeMessage(APIView):
    """
    API endpoint to view messages.

    Requires the authenticated user to retrieve their messages.

    Returns a list of serialized message data.
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request):
        """
        Handle POST requests to retrieve messages for the authenticated user.

        Parameters:
        - request: The incoming request object.

        Returns:
        - Response: JSON response containing a list of serialized message data.
        """
        # Get the authenticated user from the request
        user = request.user
        receiver_id = request.data.get("receiver_id")
        try:
            # Try to get the receiver user object
            receiver = User.objects.get(pk=receiver_id)
        except User.DoesNotExist:
            return Response({"ERROR":"Receiver user does not exist"})

        # Retrieve messages for the authenticated user from both sender and receiver
        messages = Message.objects.filter(
            (Q(sender=user.id, receiver=receiver) | Q(sender=receiver, receiver=user.id))
        ).order_by("-id")

        # Serialize the messages
        serializer = Seemessagesearializer(messages, many=True)

        # Return the serialized data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdatePassword(APIView):
    """
    API endpoint to update a user's password.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Update the user's password.

        Parameters:
        - new_password: New password for the user.
        - previous_password: Previous password for the user.

        Returns:
        - 200 OK: Password updated successfully.
        - 400 Bad Request: If the request is missing required parameters, or previous password does not match.
        """
        user = request.user  # Get the current authenticated user

        serializer = UserUpdatepasswordSerializer(user, data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password updated successfully."},
                            status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        instance = self.request.user  # Get the current authenticated user
        serializer = UserSerializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve the profile of the authenticated user
        return self.request.user


class OrderUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Update user information in an existing order using POST method.

        Parameters:
        - order_id (int): The ID of the order to be updated.

        Returns:
        - Response: Serialized order data if successful, error response otherwise.
        """

        # Extract data from the request
        order_id = request.data.get('order_id')

        # Validate that order_id is not empty and is a valid integer
        if not order_id or not order_id.isdigit():
            return Response({"error": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the authenticated user
            user = request.user

            # Retrieve the order based on the provided order_id
            order = Order.objects.get(id=int(order_id), user=user)

            # Use the OrderUpdateSerializer to update user information
            serializer = OrderUpdateSerializer(instance=order, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            # Return a 404 error response if the specified order does not exist
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


class GoogleAuthAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        id_token = request.data.get('idToken')

        try:
            # Verify the ID token
            id_info = verify_oauth2_token(id_token, requests.Request())
            # Get user info
            user_email = id_info['email']
            user_image_url = id_info['picture']
            name = id_info['name']
            
            # Generate a random password
            random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            random_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

            # Check if the user exists in the database, or create a new one
            try:
                user, created = User.objects.get_or_create(email=user_email, defaults={'username': user_email.split('@')[0], 'password': random_password}, full_name=name, is_buyer=True)
            
                # Download and save the profile picture
                image_response = efwe.get(user_image_url)
                
                if image_response.status_code == 200:
                    parsed_url = urlparse(user_image_url)
                    file_extension = os.path.splitext(parsed_url.path)[1]
                    if not file_extension:
                        file_extension = '.jpg'  # If no extension found, default to jpg
                    file_path = os.path.join(settings.MEDIA_ROOT, random_filename + file_extension)
                    with open(file_path, 'wb') as f:
                        f.write(image_response.content)
                    user.profile = random_filename + file_extension
                    user.save()
                else:
                    # Unable to download image
                    return Response(data={"error": "Unable to download profile picture"}, status=status.HTTP_400_BAD_REQUEST)
                
                token = get_tokens_for_user(user)
                response_data = {
                    'response': 'Account Created',
                    'id': user.id,
                    'username': user.username,
                    'profile_image': user.profile.url,
                    'email': user.email,
                    'token': token
                }
                # Return some response or token
                return Response(data={"message": response_data}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                # User account already exists, handle login
                token = get_tokens_for_user(user)
                response_data2 = {
                    'response': 'Account Logged In',
                    'username': user.username,
                    'profile_image': user.profile.url,  # Return profile picture URL
                    'email': user.email,
                    'id': user.id,
                    'token': token
                }
                return Response(response_data2, status=status.HTTP_200_OK)
                
        except ValueError as e:
            # Invalid token
            return Response(data={"error": f"Invalid token {e}"}, status=status.HTTP_400_BAD_REQUEST)

class SpecificUserChat(APIView):
    permission_classes = [IsAuthenticated]

    def get_receiver_info(self, receiver):
        return {
            'receiver_name': receiver.username,
            'receiver_id': receiver.id,
            'receiver_image': receiver.profile.url if receiver.profile else None,
        }

    def post(self, request):
        # Retrieve all messages sent by the authenticated user (sender)
        sender = request.user
        # Get the latest message for each unique receiver
        latest_messages = Message.objects.filter(sender=sender).values('receiver').annotate(
            max_timestamp=Max('timestamp'), last_message=Max('content')
        )
        
        # Serialize the receiver information along with the last message and its timestamp
        receiver_info_list = []
        for item in latest_messages:
            receiver = User.objects.get(id=item['receiver'])
            receiver_info = self.get_receiver_info(receiver)
            receiver_info['last_message'] = item['last_message']
            receiver_info['timestamp_last_message'] = item['max_timestamp']
            receiver_info_list.append(receiver_info)
        
        # Return the serialized receiver information in the response
        return Response(receiver_info_list, status=status.HTTP_200_OK)