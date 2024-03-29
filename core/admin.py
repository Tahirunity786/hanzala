from django.contrib import admin
from core.models import UserProducts, ProductImage,Order,FavouritesSaved, Reviews, Message, User


class ProductImageInline(admin.TabularInline):  # or admin.StackedInline
    model = ProductImage
    extra = 1  # Set the number of empty forms to display for additional images

class UserProductsAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

admin.site.register(UserProducts)
admin.site.register(ProductImage)
# admin.site.register(UserProfile)
admin.site.register(Order)
admin.site.register(FavouritesSaved)
admin.site.register(Reviews)
admin.site.register(Message)
admin.site.register(User)
