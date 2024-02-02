import datetime
from django.contrib.auth import get_user_model
from rest_framework import serializers
from core.models import Order
# from payments.models import Payment
User = get_user_model()


def check_expiry_month(value):
    if not 1 <= int(value) <= 12:
        raise serializers.ValidationError("Invalid expiry month.")


def check_expiry_year(value):
    today = datetime.datetime.now()
    if not int(value) >= today.year:
        raise serializers.ValidationError("Invalid expiry year.")


def check_cvc(value):
    if not 3 <= len(value) <= 4:
        raise serializers.ValidationError("Invalid cvc number.")


def check_payment_method(value):
    payment_method = value.lower()
    if payment_method not in ["card"]:
        raise serializers.ValidationError("Invalid payment_method.")

class CardInformationSerializer(serializers.Serializer):
    card_number = serializers.CharField(max_length=150, required=True)
    exp_month = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_expiry_month],
    )
    exp_year = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_expiry_year],
    )
    cvc = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_cvc],
    )
    
class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')
        
        
class PaymentSerializer(serializers.ModelSerializer):
    user = Userserializer()
    class Meta:
        model = Order
        fields = '__all__'