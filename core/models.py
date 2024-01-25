from django.db import models
from django.contrib.auth.models import User

        
class ProductImage(models.Model):
    image = models.ImageField(upload_to='product_images/', verbose_name="Product Image")

class UserProducts(models.Model):
    def default_user_image():
        return "user.png"
    
    category = models.CharField(max_length=100, default=None)
    user_image = models.ImageField(upload_to='product_images/user', verbose_name="Product user Image", default=default_user_image)
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
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product_title} - {self.product_token}"
    

    class Meta:
        verbose_name_plural = "User Products"
    
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(UserProducts, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activate_order = models.CharField(max_length=100,default=False, db_index=True)
    received_order = models.CharField(max_length=100,default=False, db_index=True)
    canceled_order = models.CharField(max_length=100,default=False, db_index=True)
    purchased_quantity = models.IntegerField(default=None, db_index=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.product.product_title}"
    
    

class FavouritesSaved(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    product = models.ForeignKey('UserProducts', on_delete=models.CASCADE, related_name="favorited_by")
    saved_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Favorite Saved"
        verbose_name_plural = "Favorites Saved"
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.product.name} ({self.saved_at})"


class Reviews(models.Model):
    reviews_giver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_given")
    reviewer_message = models.TextField(verbose_name="Message")
    
    def __str__(self):
        return f"{self.reviews_giver.username} has given {self.reviewer_message}"


