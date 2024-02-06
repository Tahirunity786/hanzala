from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.
class PaymentModifier(models.Model):
    who_update_fee_one_payment = models.ForeignKey(User, on_delete=models.CASCADE)
    protection_fee = models.IntegerField(default=5)
    delivery_fee = models.IntegerField(default=5)