from rest_framework import serializers
from core.models import User


class CreateUserSearializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user.

    This serializer is used to validate and create a new user based on the provided data.
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'otp', 'password')

    def create(self, validated_data):
        """
        Create a new user instance.

        Parameters:
        - validated_data (dict): Validated data containing user details.

        Returns:
        - User: The newly created user instance.
        """
        # Getting password from validated data
        password = validated_data.pop('password', None)

        # Creating an instance of the user model
        instance = self.Meta.model(**validated_data)

        # Getting username and email
        user_name = validated_data.get('username', None)
        user_email = validated_data.get('email', None)

        if user_name:
            instance.email = user_email
            instance.username = user_name
        else:
            raise ValueError("User not found")

        if password:
            instance.set_password(password)
        else:
            raise ValueError("Password not given")

        instance.save()

        return instance