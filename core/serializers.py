from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import FavouritesSaved, Message, Order, ProductImage, Reviews, UserProducts, Info_user

User = get_user_model()

class CreateUserSearializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user.

    This serializer validates the input data for creating a new user and
    utilizes Django's built-in UserManager for secure password handling.

    Args:
        serializers.ModelSerializer: A subclass of the ModelSerializer in Django REST framework.

    Attributes:
        password2 (serializers.CharField): A field for confirming the password.

    Raises:
        serializers.ValidationError: Raised when passwords do not match or the user already exists.

    Returns:
        User: The newly created user instance.

    Example:
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            # Additional logic with the created user.

    """

    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    extra_kwargs = {
        'password': {'write_only': True}
    }

    def save(self):
        """
        Save method for creating a new user.

        This method validates the password confirmation and checks for existing users
        before creating a new user with the provided data.

        Returns:
            User: The newly created user instance.

        Raises:
            serializers.ValidationError: Raised when passwords do not match or the user already exists.

        """
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'Error': 'Passwords do not match'})

        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({'Error': 'User already exists'})

        account = User.objects.create_user(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
            password=self.validated_data['password'],
            is_active = True,
            is_verified=True,
            is_buyer=True,
        )

        return account

    
    
class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Attributes:
        password (str): The user's password.
    """
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'password']


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for product images.

    Attributes:
        product (int): The ID of the associated product.
        image (str): The image URL or path.
    """
    class Meta:
        model = ProductImage
        fields = ("product", "image")


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for user products.

    Attributes:
        user_image (str): The user's image URL or path.
        product_title (str): The title of the product.
        product_description (str): The description of the product.
        condition (str): The condition of the product.
        brand (str): The brand of the product.
        color (str): The color of the product.
        model (str): The model of the product.
        ram (int): The RAM size of the product.
        storage (int): The storage capacity of the product.
        battery_capacity (int): The battery capacity of the product.
        category (str): The category of the product.
        price (float): The price of the product.
    """
    class Meta:
        model = UserProducts
        fields = ["user_image", "product_title", "product_description", "condition", "brand", "color", "model", "ram", "storage",'price','category', "battery_capacity",'latitude','longitude', 'product_address']

    def create(self, validated_data):
        """
        Create and save a new UserProducts instance.

        Args:
            validated_data (dict): Validated data for creating the instance.

        Returns:
            UserProducts: The created UserProducts instance.
        """
        # Extracting fields from validated data
        product_title = validated_data.pop('product_title', None)
        user_image = validated_data.pop('user_image', None)
        product_description = validated_data.pop('product_description', None)
        condition = validated_data.pop('condition', None)
        brand = validated_data.pop('brand', None)
        color = validated_data.pop('color', None)
        model = validated_data.pop('model', None)
        ram = validated_data.pop('ram', None)
        storage = validated_data.pop('storage', None)
        battery_capacity = validated_data.pop('battery_capacity', None)
        category = validated_data.pop('category', None)
        price = validated_data.pop('price', None)
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        product_address = validated_data.pop('product_address', None)

        # Optimizing category
        category_string = category.replace(" ", "").lower()

        # Creating the instance with the remaining validated data
        instance = self.Meta.model(**validated_data)
        instance.user_image = user_image
        instance.product_title = product_title
        instance.product_description = product_description
        instance.brand = brand
        instance.condition = condition
        instance.color = color
        instance.model = model
        instance.ram = ram
        instance.storage = storage
        instance.battery_capacity = battery_capacity
        instance.category = category_string
        instance.price = price
        instance.latitude = latitude
        instance.longitude = longitude
        instance.product_address = product_address
        instance.total_price = 1
        instance.save()

        return instance

    def update(self, instance, validated_data):
        """
        Update and save an existing UserProducts instance.

        Args:
            instance (UserProducts): The existing instance to be updated.
            validated_data (dict): Validated data for updating the instance.

        Returns:
            UserProducts: The updated UserProducts instance.
        """
        images_data = validated_data.pop('images', [])
        
        instance.product_title = validated_data.get('product_title', instance.product_title)
        instance.product_description = validated_data.get('product_description', instance.product_description)
        instance.condition = validated_data.get('condition', instance.condition)
        instance.brand = validated_data.get('brand', instance.brand)
        instance.color = validated_data.get('color', instance.color)
        instance.model = validated_data.get('model', instance.model)
        instance.ram = validated_data.get('ram', instance.ram)
        instance.storage = validated_data.get('storage', instance.storage)
        instance.battery_capacity = validated_data.get('battery_capacity', instance.battery_capacity)

        for image_data in images_data:
            ProductImage.objects.create(user_products=instance, **image_data)

        instance.save()
        return instance

    def delete(self, instance):
        """
        Delete the UserProducts instance.

        Args:
            instance (UserProducts): The UserProducts instance to be deleted.
        """
        instance.delete()
        
class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProductImage model.
    """
    class Meta:
        model = ProductImage
        fields = ('image',)

class UserProductsSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProducts model.
    Includes ProductImageSerializer as a nested serializer for the 'product_image' field.
    """
    product_image = ProductImageSerializer(many=True, read_only=True)

    # Add a new field 'username' to display the actual username
    username = serializers.SerializerMethodField()

    class Meta:
        model = UserProducts
        fields = '__all__'

    def get_username(self, obj):
        """
        Custom method to retrieve the username from the related User model.
        """
        return obj.username.username if obj.username else None
    
    
class Useraddsearializer(serializers.ModelSerializer):
    """
    Serializer for the UserProducts model (used for adding a user).
    Includes ProductImageSerializer as a nested serializer for the 'product' field.
    """
    product = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = UserProducts
        fields = '__all__'

class Userfavouriteproduct(serializers.ModelSerializer):
    """
    Serializer for the FavouritesSaved model.
    """
    product = UserProductsSerializer()  # Remove many=True

    class Meta:
        model = FavouritesSaved
        fields = ('user', 'product', 'saved_at')

    def create(self, validated_data):
        """
        Custom create method to handle FavouritesSaved instance creation.
        """
        user = validated_data['user']
        product_data = validated_data['product']

        # Assuming product_data is a dictionary containing UserProducts data
        # If product_data is a UserProducts instance, you can use it directly
        product_instance = UserProducts.objects.create(**product_data)

        # Create and return the FavouritesSaved instance
        return FavouritesSaved.objects.create(user=user, product=product_instance)

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.
    Includes UserProductsSerializer as a nested serializer for the 'product' field.
    """
    product = UserProductsSerializer()

    class Meta:
        model = Order
        fields = '__all__'

class ReviewsSerializer(serializers.ModelSerializer):
    """
    Serializer for the Reviews model.
    """
    class Meta:
        model = Reviews
        fields = ('reviews_giver', 'review_at_product', 'reviews', 'reviewer_message', 'review_given_at')

class DeleteProductSerializer(serializers.Serializer):
    """
    Serializer for deleting a product.
    """
    id = serializers.IntegerField()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = ('id', 'username')

class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    Includes UserSerializer as nested serializers for the 'sender' and 'receiver' fields.
    """
    sender = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = Message
        fields = ('id', 'sender', 'receiver', 'content', 'timestamp',)

class GoogleSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model (used for Google login).
    """
    class Meta:
        model = User
        fields = ['username', 'email']

class InfouserSerializer(serializers.ModelSerializer):
    """
    Serializer for the Info_user model.
    Includes fields for user information.
    """
    full_name = serializers.CharField(max_length=100, write_only=True)
    country = serializers.CharField(max_length=100, write_only=True)
    address1 = serializers.CharField(max_length=100, write_only=True)
    postal_code = serializers.IntegerField(write_only=True)
    latitude1 = serializers.CharField(max_length=100, write_only=True)
    latitude1 = serializers.CharField(max_length=100, write_only=True)

    class Meta:
        model = Info_user
        fields = ("full_name", "country", "address1", "address2", "postal_code", "latitude1", "latitude2")

    def create(self, validated_data):
        """
        Custom create method to handle Info_user instance creation.
        """
        # Extract user from request
        user = self.context['request'].user

        # Include user in validated_data
        validated_data['user'] = user

        # Create and return the Info_user instance
        return super(InfouserSerializer, self).create(validated_data)
    


class Seemessagesearializer(serializers.ModelSerializer):
    
    class Meta:
        model = Message
        fields = ('id', 'content', 'timestamp')

class notificationsearializer(serializers.Serializer):
    title = serializers.CharField(max_length=150, required=True)
    body = serializers.CharField(max_length=500, required=True)
    token = serializers.CharField(max_length=500, required=True)


class UserUpdatepassword(serializers.ModelSerializer):
    password2 = serializers.CharField(require=True, write_only=True)
    class Meta:
        model = User
        fields = ['password', 'password2']  