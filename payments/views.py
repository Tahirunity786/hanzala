import logging
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CardInformationSerializer, PaymentSerializer
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from core.models import UserProducts, Order
from django.core.exceptions import ObjectDoesNotExist
import stripe





logger = logging.getLogger(__name__)
# stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

class PaymentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CardInformationSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            data_dict = serializer.validated_data

            product_id = request.data.get('product_id')

            # Check if the product exists
            try:
                prod = UserProducts.objects.get(id=product_id)
            except ObjectDoesNotExist:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

            # Create a PaymentIntent with Stripe
            payment_method = stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": data_dict.get('card_number'),
                    "exp_month": data_dict.get('exp_month'),
                    "exp_year": data_dict.get('exp_year'),
                    "cvc": data_dict.get('cvc'),
                },
            )

            payment_intent = stripe.PaymentIntent.create(
                amount=int(prod.price * 100),  # Amount in cents
                currency='usd',
                payment_method_types=["card"],
                payment_method=payment_method.id
            )

            # Confirm the PaymentIntent (3D Secure authentication, if required)
            payment_intent.confirm(payment_method='pm_card_visa')

            # Record the payment in your database
            payment = Order.objects.create(
                user=request.user,
                total_price=prod.price,
                product=prod,
                activate_order="active",
                purchased_quantity=1,
                payment_method="online"
            )

            # Serialize the payment data for the response
            payment_serializer = PaymentSerializer(payment)

            return Response({'payment': payment_serializer.data, 'client_secret': payment_intent.client_secret}, status=status.HTTP_201_CREATED)

        except stripe.error.CardError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the exception for debugging purposes
            # Consider using a logging library or saving logs to a file
            print(f"Unexpected error: {str(e)}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)