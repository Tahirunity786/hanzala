from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from core.serializers import CreateUserSearializer, ProductImageSerializer, ProductSerializer, UserProductsSerializer,Useraddsearializer
from core.rendenerers import UserRenderer
from random import randint
from core.tokken_agent import get_tokens_for_user
from rest_framework.permissions import IsAuthenticated
import uuid
from core.models import ProductImage, UserProducts
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from rest_framework import viewsets
from collections import defaultdict
from django.db.models import Prefetch
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
    """
    API endpoint for retrieving products associated with the authenticated user.
    Requires authentication.
    """

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        """
        Get the list of products associated with the authenticated user.

        Returns:
            Response: A JSON response with the serialized list of user products.
        """
        user_id = request.user.id

        # Ensure user_id is provided in the request
        if not user_id:
            return Response({"error": "User ID is required in the request data."}, status=400)

        # Use get_object_or_404 to handle User.DoesNotExist exception
        user = get_object_or_404(User, pk=user_id)

        # Use select_related to fetch related data in a single query
        queryset = UserProducts.objects.filter(username=user).select_related('product')
        serializer = UserProductsSerializer(queryset, many=True)

        return Response(serializer.data, status=200)

