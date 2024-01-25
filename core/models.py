from django.db import models
from django.contrib.auth.models import User

        
class ProductImage(models.Model):
    image = models.ImageField(upload_to='product_images/', verbose_name="Product Image")

class UserProducts(models.Model):
    category = models.CharField(max_length=100, default=None)
  
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products_created", default="", blank=True, null=True)
    product_image = models.ManyToManyField(ProductImage, related_name="products_images", blank=True)
    product_token = models.CharField(max_length=200, default=None, db_index=True, blank=True, null=True)
    product_title = models.CharField(max_length=150, default=None, db_index=True)
    product_description = models.TextField(verbose_name="Product Description", default=None,)
    condition = models.CharField(max_length=20, default="Not decided", verbose_name="Condition")
    brand = models.CharField(max_length=100, default="Not decided", verbose_name="Brand", db_index=True)
    color = models.CharField(max_length=100, default=None)
    model = models.CharField(max_length=100, default=None)
    ram = models.CharField(max_length=100, default=None)
    storage = models.BigIntegerField(default=0)
    battery_capacity = models.CharField(max_length=20, default=None)
    price = models.IntegerField(default=None)
    
    def __str__(self):
        return f"{self.product_title} - {self.product_token}"

    class Meta:
        verbose_name_plural = "User Products"
    
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(UserProducts, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activate_order = models.BooleanField(default=False, db_index=True)
    received_order = models.BooleanField(default=False, db_index=True)
    canceled_order = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.product.product_title}"

class FavouritesSaved(models.Model):  # Updated class name
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_products")
    product = models.ForeignKey(UserProducts, on_delete=models.CASCADE, related_name="favorited_by")
    saved_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s saved products"

class Reviews(models.Model):
    reviews_giver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_given")
    reviewer_message = models.TextField(verbose_name="Message")
    
    def __str__(self):
        return f"{self.reviews_giver.username} has given {self.reviewer_message}"

class UserProfile(models.Model):
    BILLING_INFO_CHOICES = [
        ('cash', 'Cash'),
        ('Google pay', 'Google pay'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_index=True)
    my_ads = models.ManyToManyField(UserProducts, related_name='user_ads', blank=True)
    orders = models.ManyToManyField(Order, related_name='user_orders', blank=True)
    fav_saved_items = models.ManyToManyField(FavouritesSaved, related_name='user_saved', blank=True)
    reviews = models.ManyToManyField(Reviews, related_name='user_reviews', blank=True)
    billing_info = models.CharField(max_length=100, choices=BILLING_INFO_CHOICES, default='Not decided', db_index=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
