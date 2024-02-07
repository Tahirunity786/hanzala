from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.


class PaymentDetails(models.Model):
    accounttitle = models.CharField(max_length = 100, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length = 100, default="")
    email = models.EmailField()
    card_number = models.CharField(max_length = 150, default="")
    cvc = models.IntegerField()
    expiry = models.CharField(max_length=50, default="")
