from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CardInformationSerializer
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import stripe


class PaymentAPI(APIView):
    """
    API endpoint for processing card payments using the Stripe API.

    Parameters:
    - `card_number` (str): The card number.
    - `expiry_month` (str): The expiration month of the card.
    - `expiry_year` (str): The expiration year of the card.
    - `cvc` (str): The card's CVC (Card Verification Code).

    Note: This endpoint uses the Stripe API for processing payments and requires a valid API key to be set.
    """

    serializer_class = CardInformationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle POST requests for processing card payments.

        Returns:
        - Response: JSON response indicating the success or failure of the payment process.
        """
    
        serializer = self.serializer_class(data=request.data)
        response = {}

        if serializer.is_valid():
            data_dict = serializer.data
            stripe.api_key = settings.STRIPE_API_KEY
            response = self.stripe_card_payment(data_dict)
        else:
            response = {
                'errors': serializer.errors,
                'status': status.HTTP_400_BAD_REQUEST
            }

        return Response(response)

    def stripe_card_payment(self, data_dict):
        """
        Process card payment using the Stripe API.

        Parameters:
        - `data_dict` (dict): A dictionary containing card information.

        Returns:
        - dict: A JSON response indicating the success or failure of the payment process.
        """
        try:
            card_details = {
                "type": "card",
                "card": {
                    "number": data_dict['card_number'],
                    "exp_month": data_dict['expiry_month'],
                    "exp_year": data_dict['expiry_year'],
                    "cvc": data_dict['cvc'],
                },
            }
            #  you can also get the amount from the database by creating a model
            payment_intent = stripe.PaymentIntent.create(
                amount=data_dict['amount'],
                currency='dllr',
            )
            payment_intent_modified = stripe.PaymentIntent.modify(
                payment_intent['id'],
                payment_method=card_details['id'],
            )

            try:
                payment_confirm = stripe.PaymentIntent.confirm(
                    payment_intent['id']
                )
                payment_intent_modified = stripe.PaymentIntent.retrieve(payment_intent['id'])
            except stripe.error.CardError as e:
                payment_intent_modified = stripe.PaymentIntent.retrieve(payment_intent['id'])
                payment_confirm = {
                    "stripe_payment_error": "Failed",
                    "code": e.code,
                    "message": e.error.message,
                    'status': "Failed"
                }

            if payment_intent_modified and payment_intent_modified['status'] == 'succeeded':
                response = {
                    'message': "Card Payment Success",
                    'status': status.HTTP_200_OK,
                    "card_details": card_details,
                    "payment_intent": payment_intent_modified,
                    "payment_confirm": payment_confirm
                }
            else:
                response = {
                    'message': "Card Payment Failed",
                    'status': status.HTTP_400_BAD_REQUEST,
                    "card_details": card_details,
                    "payment_intent": payment_intent_modified,
                    "payment_confirm": payment_confirm
                }
        except stripe.error.CardError:
            response = {
                'error': "Your card number is incorrect",
                'status': status.HTTP_400_BAD_REQUEST,
                "payment_intent": {"id": "Null"},
                "payment_confirm": {'status': "Failed"}
            }

        return response
