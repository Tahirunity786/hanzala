# class PaymentAPI(APIView):
#     """
#     API endpoint for processing card payments using the Stripe API.

#     Parameters:
#     - `card_number` (str): The card number.
#     - `expiry_month` (str): The expiration month of the card.
#     - `expiry_year` (str): The expiration year of the card.
#     - `cvc` (str): The card's CVC (Card Verification Code).

#     Note: This endpoint uses the Stripe API for processing payments and requires a valid API key to be set.
#     """

#     serializer_class = CardInformationSerializer
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         """
#         Handle POST requests for processing card payments.

#         Returns:
#         - Response: JSON response indicating the success or failure of the payment process.
#         """
    
#         serializer = self.serializer_class(data=request.data)
#         response = {}

#         if serializer.is_valid():
#             data_dict = serializer.data
#             stripe.api_key = settings.STRIPE_SECRET_KEY
#             response = self.stripe_card_payment(data_dict)
#         else:
#             response = {
#                 'errors': serializer.errors,
#                 'status': status.HTTP_400_BAD_REQUEST
#             }

#         return Response(response)

#     def stripe_card_payment(self, data_dict):
#         """
#         Process card payment using the Stripe API.

#         Parameters:
#         - `data_dict` (dict): A dictionary containing card information.

#         Returns:
#         - dict: A JSON response indicating the success or failure of the payment process.
#         """
#         try:
#             card_details = {
#                 "type": "card",
#                 "card": {
#                     "number": data_dict['card_number'],
#                     "exp_month": data_dict['expiry_month'],
#                     "exp_year": data_dict['expiry_year'],
#                     "cvc": data_dict['cvc'],
#                 },
#             }
#             #  you can also get the amount from the database by creating a model
#             payment_intent = stripe.PaymentIntent.create(
#                 amount=data_dict['amount'],
#                 currency='usd',
#             )
#             payment_intent_modified = stripe.PaymentIntent.modify(
#                 payment_intent['id'],
#                 payment_method=card_details['id'],
#             )

#             try:
#                 payment_confirm = stripe.PaymentIntent.confirm(
#                     payment_intent['id']
#                 )
#                 payment_intent_modified = stripe.PaymentIntent.retrieve(payment_intent['id'])
#             except stripe.error.CardError as e:
#                 payment_intent_modified = stripe.PaymentIntent.retrieve(payment_intent['id'])
#                 payment_confirm = {
#                     "stripe_payment_error": "Failed",
#                     "code": e.code,
#                     "message": e.error.message,
#                     'status': "Failed"
#                 }

#             if payment_intent_modified and payment_intent_modified['status'] == 'succeeded':
#                 response = {
#                     'message': "Card Payment Success",
#                     'status': status.HTTP_200_OK,
#                     "card_details": card_details,
#                     "payment_intent": payment_intent_modified,
#                     "payment_confirm": payment_confirm
#                 }
#             else:
#                 response = {
#                     'message': "Card Payment Failed",
#                     'status': status.HTTP_400_BAD_REQUEST,
#                     "card_details": card_details,
#                     "payment_intent": payment_intent_modified,
#                     "payment_confirm": payment_confirm
#                 }
#         except stripe.error.CardError:
#             response = {
#                 'error': "Your card number is incorrect",
#                 'status': status.HTTP_400_BAD_REQUEST,
#                 "payment_intent": {"id": "Null"},
#                 "payment_confirm": {'status': "Failed"}
#             }
#         except ValueError as e:
#         # Handle the case where the amount is less than 50 cents
#             response = {
#                 'error': str(e),
#                 'status': status.HTTP_400_BAD_REQUEST,
#                 "payment_intent": {"id": "Null"},
#                 "payment_confirm": {'status': "Failed"}
#             }
    
#         return response

# class PaymentView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = CardInformationSerializer

#     def post(self, request):
#         try:
#             serializer = self.serializer_class(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             data_dict = serializer.validated_data

#             product_id = request.data.get('product_id')

#             if product_id:
#                 prod = UserProducts.objects.get(id=product_id)
#             else:
#                 return Response({"Error": "The selected product has been removed or sold out"}, status=status.HTTP_400_BAD_REQUEST)

#             # Create a PaymentIntent with Stripe
#             payment_method = stripe.PaymentMethod.create(
#                 type="card",
#                 card={
#                     "number": data_dict.get('card_number'),
#                     "exp_month": data_dict.get('exp_month'),
#                     "exp_year": data_dict.get('exp_year'),
#                     "cvc": data_dict.get('cvc'),
#                 },
#             )

#             payment_intent = stripe.PaymentIntent.create(
#                 amount=int(prod.price * 100),  # Amount in cents
#                 currency='usd',
#                 payment_method=payment_method['id'],
#                 confirmation_method='manual',
#             )

#             # Confirm the PaymentIntent (3D Secure authentication, if required)
#             payment_intent.confirm(payment_method='pm_card_visa')

#             # Record the payment in your database
#             payment = Order.objects.create(
#                 user=request.user,
#                 total_price=prod.price,
#                 product=prod,
#                 activate_order="active",
#                 purchased_quantity=1,
#                 payment_method="online"
#             )

#             # Serialize the payment data for the response
#             payment_serializer = PaymentSerializer(payment)

#             return Response({'payment': payment_serializer.data, 'client_secret': payment_intent.client_secret}, status=status.HTTP_201_CREATED)

#         except stripe.error.CardError as e:
#             body = e.error.payment_intent
#             return Response({'error': str(body)}, status=status.HTTP_400_BAD_REQUEST)
#         except UserProducts.DoesNotExist:
#             return Response({"Error": "Product not found"}, status=status.HTTP_400_BAD_REQUEST)
#         except stripe.error.StripeError as e:
#             logger.error(f"Stripe error: {str(e)}")
#             return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             logger.error(f"Unexpected error: {str(e)}")
#             return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CardInformationSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            response = {}

            if serializer.is_valid():
                data_dict = serializer.data

                product_id = request.data.get('product_id')

                if product_id:
                    prod = UserProducts.objects.get(id=product_id)
                else:
                    return Response({"Error": "May be Your selected product removed or soldout"}, status=status.HTTP_400_BAD_REQUEST)

                # Use test card tokenization instead of raw credit card details
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(prod.price * 100),  # Amount in cents
                    currency='usd',
                    payment_method_types=["card"],
                    payment_method=data_dict.get('payment_method_token')  # Use the token received from your frontend
                )

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
        except UserProducts.DoesNotExist:
            return Response({"Error": "Product not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)