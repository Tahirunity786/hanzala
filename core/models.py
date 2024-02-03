from django.db import models
from core.manager import CustomUserManager
from django.contrib.auth.models import AbstractUser,Group, Permission



class User(AbstractUser):
    # General Information about the user
    profile = models.ImageField(upload_to="profile/images", blank=True, null=True)
    full_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True, db_index=True)
    email = models.EmailField(null=False, unique=True)  
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(default=None, null=True)
    is_blocked = models.BooleanField(default=False, null=True)
    is_verified = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=False)
    password = models.CharField(max_length=200,db_index=True, default=None )
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    # Unique related_name for groups and user_permissions
    groups = models.ManyToManyField(Group, related_name='user_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='user_permissions', blank=True)
  

        
class ProductImage(models.Model):
    """
    Model to represent images associated with products.
    """
    image = models.ImageField(upload_to='product_images/', verbose_name="Product Image")

class UserProducts(models.Model):
    """
    Model to represent user-created products.
    """
    def default_user_image():
        return "user.png"
    
    category = models.CharField(max_length=100, default=None)
    user_image = models.ImageField(upload_to='product_images/user', verbose_name="Product user Image", default=default_user_image)
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products_created", default="", blank=True, null=True)
    product_image = models.ManyToManyField(ProductImage, related_name="products_images", blank=True)
    product_token = models.CharField(max_length=200, default=None, db_index=True, blank=True, null=True)
    product_title = models.CharField(max_length=150, default=None, db_index=True)
    product_description = models.TextField(verbose_name="Product Description", default=None,)
    product_address= models.TextField(verbose_name="Product address", default=None,)
    condition = models.CharField(max_length=20, default="Not decided", verbose_name="Condition")
    brand = models.CharField(max_length=100, default="Not decided", verbose_name="Brand", db_index=True)
    color = models.CharField(max_length=100, default=None)
    model = models.CharField(max_length=100, default=None)
    ram = models.CharField(max_length=100, default=None)
    storage = models.BigIntegerField(default=0)
    battery_capacity = models.CharField(max_length=20, default=None)
    price = models.IntegerField(default=None)
    date = models.DateTimeField(auto_now_add=True)
    latitude = models.CharField(max_length=100, default=False, db_index=True)
    longitude = models.CharField(max_length=100, default=False, db_index=True)
    notification_token = models.CharField(max_length=200, default=False, db_index=True)
    total_price = models.IntegerField(default=1)
    def __str__(self):
        """
        String representation of the UserProducts object.
        """
        return f"{self.product_title} - {self.product_token}"

    class Meta:
        verbose_name_plural = "User Products"
    
class Order(models.Model):
    """
    Model representing an order made by a user for a specific product.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('UserProducts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activate_order = models.CharField(max_length=100, default=False, db_index=True)
    received_order = models.CharField(max_length=100, default=False, db_index=True)
    canceled_order = models.CharField(max_length=100, default=False, db_index=True)
    total_price = models.IntegerField(default=0)
    payment_method = models.CharField(max_length=100, default=False, db_index=True)

    def __str__(self):
        """
        String representation of the Order object.
        """
        return f"Order #{self.id} - {self.user.username} - {self.product.product_title}"

class FavouritesSaved(models.Model):
    """
    Model representing a user's favorite product saved at a specific time.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    product = models.ForeignKey('UserProducts', on_delete=models.CASCADE, related_name="favorited_by")
    saved_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Favorite Saved"
        verbose_name_plural = "Favorites Saved"
        ordering = ['-saved_at']

    def __str__(self):
        """
        String representation of the FavouritesSaved object.
        """
        return f"{self.user.username}'s favorite: {self.product.name} ({self.saved_at})"


class Reviews(models.Model):
    """
    Model to represent reviews given by users on products.

    Attributes:
        reviews_giver (User): The user who gives the review.
        review_at_product (UserProducts): The product being reviewed.
        reviews (int): The numerical rating given in the review (default is 0).
        reviewer_message (str): The text message provided by the reviewer.
        review_given_at (datetime): The timestamp when the review was given (auto-generated).
    """
    reviews_giver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_given")
    review_at_product = models.ForeignKey(UserProducts, on_delete=models.CASCADE, related_name="reviews_at_product", null=True)
    reviews = models.IntegerField(default=0)
    reviewer_message = models.TextField(verbose_name="Message")
    review_given_at = models.DateTimeField(auto_now=True)


class Message(models.Model):
    """
    Model to represent messages exchanged between users.

    Attributes:
        sender (User): The user sending the message.
        receiver (User): The user receiving the message.
        content (str): The text content of the message.
        is_read (bool): Indicates whether the message has been read (default is False).
        timestamp (datetime): The timestamp when the message was sent (auto-generated).

    Methods:
        __str__(): String representation of the message, useful for debugging and display.
    """
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE, default=None)
    order_id = models.CharField(max_length=100, default=False, db_index=True)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the message.

        Returns:
            str: String representation of the message, including sender, receiver, and content.
        """
        return f"{self.sender} to {self.receiver}: {self.content}"


class Info_user(models.Model):
    """
    Model to store additional information about a user.

    Attributes:
        user (User): ForeignKey to the User model, establishing a relationship.
        full_name (str): User's full name.
        country (str): User's country.
        address1 (str): First line of the user's address.
        address2 (str, optional): Second line of the user's address (can be None).
        postal_code (int): User's postal code.
        latitude1 (str): Latitude information related to address1.
        latitude2 (str): Latitude information related to address2.

    Note:
        This model is related to the built-in User model in Django.
    """

    user = models.ForeignKey(User, related_name='User_profile', on_delete=models.CASCADE, default=None)
    full_name = models.CharField(max_length=100, default=False, db_index=True)
    country = models.CharField(max_length=100, default=False, db_index=True)
    address1 = models.TextField()
    address2 = models.TextField(null=True)
    postal_code = models.IntegerField(default=0)
    latitude1 = models.CharField(max_length=100, default=False, db_index=True)
    latitude2 = models.CharField(max_length=100, default=False, db_index=True)