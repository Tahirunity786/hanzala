from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from core.serializers import CreateUserSearializer

from random import randint
# Create your views here.

User = get_user_model()


class CreateUser(APIView):
    """
    API endpoint to create a new user.

    This endpoint allows the creation of a new user by providing necessary details.
    """

    # Permission strategy
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST request to create a new user.

        Parameters:
        - username (str): The username of the new user.
        - email (str): The email address of the new user.
        - otp (int): The OTP (One-Time Password) for user verification.
        - password (str): The password for the new user.

        Returns:
        - HTTP 201 Created: User created successfully.
        - HTTP 400 Bad Request: User not created successfully.
        - HTTP 406 Not Acceptable: Invalid data provided.
        """

        # Getting and serializing data
        sp_user = CreateUserSearializer(data=request.data)

        if sp_user.is_valid():
            agent_of_user = sp_user.save()

            if agent_of_user:
                # Generate six-digit OTP for verification
                otp = randint(100000, 999999)

                # Here goes the email sending process

                agent_of_user.otp = otp
                agent_of_user.save()

                # Returned Created response
                return Response({"message": "User has been created successfully"}, status=status.HTTP_201_CREATED)
            else:
                # Returned Not Created response
                return Response({"message": "User not created successfully, please try again"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            # Returned Not valid data response
            return Response({"message": "User data is not valid, please try again"},
                            status=status.HTTP_406_NOT_ACCEPTABLE)