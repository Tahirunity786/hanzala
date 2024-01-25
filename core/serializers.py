from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import ProductImage, UserProducts
from rest_framework.authtoken.models import Token

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
            password=self.validated_data['password']
        )

        return account

    
    
class UserLoginSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'password']
        
        
        
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("product", "image")

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProducts
        fields = ["product_title", "product_description", "condition", "brand", "color", "model", "ram", "storage",'price','category', "battery_capacity"]

    def create(self, validated_data):
        # Extract the 'product_title' field from validated data
        product_title = validated_data.pop('product_title')
        product_description = validated_data.pop('product_description')
        condition = validated_data.pop('condition')
        brand = validated_data.pop('brand')
        color = validated_data.pop('color')
        model = validated_data.pop('model')
        ram = validated_data.pop('ram')
        storage = validated_data.pop('storage')
        battery_capacity = validated_data.pop('battery_capacity')
        category = validated_data.pop('category')
        price = validated_data.pop('price')
        
        # optimizing category
        category_string = category.replace(" ", "")
        category_string = category_string.lower()
       

        # Create the instance with the remaining validated data
        instance = self.Meta.model(**validated_data)
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
        instance.save()

        return instance


    def update(self, instance, validated_data):
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
    class Meta:
        model = ProductImage
        fields = ('image',)

class UserProductsSerializer(serializers.ModelSerializer):
    product_image = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = UserProducts
        fields = '__all__'
        
        
class Useraddsearializer(serializers.ModelSerializer):
    product_image = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = UserProducts
        fields = '__all__'