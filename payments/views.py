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
from django.contrib.auth import get_user_model
User = get_user_model()




logger = logging.getLogger(__name__)
# stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        
        # Move the product_id retrieval here
        product_id = request.data.get('product_id')

        try:
            prod = UserProducts.objects.get(id=product_id)
        except ObjectDoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user.is_blocked and not prod.is_sold:
            try:
                protection_fee = int(request.data.get('protection_fee', 5))
                delivery_fee = int(request.data.get('delivery_fee', 5))
           
                # Check if the product exists
                
                
                customer = stripe.Customer.create()
    
                ephemeralKey = stripe.EphemeralKey.create(
                    customer=customer['id'],
                    stripe_version='2023-08-16',
                )
                # Create a PaymentIntent
                payment_intent = stripe.PaymentIntent.create(
                    amount=(prod.price)*100,
                    currency="usd",
                    customer=customer['id'],
                    automatic_payment_methods={"enabled": True},
                )
    
                # You would typically pass the client_secret to the frontend
                client_secret = payment_intent.client_secret
    
                # Product management logic
                total_price = prod.price+protection_fee+delivery_fee
                # Record the payment intent ID in your database (don't capture yet)
                order = Order.objects.create(
                    user=request.user,
                    total_price=total_price,
                    product=prod,  # Change this line to assign the UserProducts instance directly
                    activate_order="active",
                    payment_method="online",
                    payment_intent_id=payment_intent.id,
                )
    
                # Serialize the payment data for the response
                payment_serializer = PaymentSerializer(order)
    
                return Response({'client_secret': client_secret,'ephemeralKey':ephemeralKey.secret,'customer':customer.id,'publishableKey':settings.STRIPE_PUBLIC_KEY, 'payment': payment_serializer.data}, status=status.HTTP_201_CREATED)
    
            except stripe.error.CardError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.RateLimitError as e:
                return Response({'error': 'Rate limit error'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            except stripe.error.InvalidRequestError as e:
                return Response({'error': 'Invalid request: {}'.format(str(e))}, status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.AuthenticationError as e:
                return Response({'error': 'Authentication error'}, status=status.HTTP_401_UNAUTHORIZED)
            except stripe.error.APIConnectionError as e:
                return Response({'error': 'API connection error'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except stripe.error.StripeError as e:
                return Response({'error': 'Stripe error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                # Log the exception for debugging purposes
                # Consider using a logging library or saving logs to a file
                print(f"Unexpected error: {str(e)}")
                return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif prod.is_sold:
            return Response({"Error": "Product was sold recently"}, status=status.HTTP_400_BAD_REQUEST)
        elif user.is_blocked:
            return Response({"Error": "You are blocked by admin so you can't buy or sell product"}, status=status.HTTP_403_FORBIDDEN)
