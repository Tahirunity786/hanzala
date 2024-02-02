from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django.conf import settings
from core.models import UserProducts, Order
from django.core.exceptions import ObjectDoesNotExist
from coreadmin.serializers import CreateUserSearializer, UserUpdateserializer, AdminMessageSerializer
from core.rendenerers import UserRenderer
from core.tokken_agent import get_tokens_for_user
from core.models import Message
from django.db.models import Min
from django.db import transaction
from django.db.models import Q

User = get_user_model()

class CreateUserView(APIView):
    """
    Class-based view for creating a new admin user account.

    This view handles the creation of a new admin user account, including validation,
    saving the user instance, and generating an authentication token.

    Methods:
        - post(request): Handles the HTTP POST request for creating a new user.

    Returns:
        Response: JSON response with account details or validation errors.

    Example:
        To create a new user, send a POST request to /create_user/ with the required data.
    """

    # Attributes
    permission_classes = [AllowAny]
    renderer_classes = [UserRenderer]

    def post(self, request, *args, **kwargs):
        """
        Handles the HTTP POST request for creating a new user.

        Args:
            request (rest_framework.request.Request): The HTTP request object.

        Returns:
            Response: JSON response with account details or validation errors.

        Raises:
            status.HTTP_201_CREATED: If the user account is successfully created.
            status.HTTP_406_NOT_ACCEPTABLE: If there are validation errors in the provided data.
        """
        serializer = CreateUserSearializer(data=request.data)

        if serializer.is_valid():
            account = serializer.save()
            tokken = get_tokens_for_user(account)

            response_data = {
                'response': 'Admin Account has been created',
                'username': account.username,
                'email': account.email,
                'id': account.id,
                'is_staff': account.is_staff,
                'token': tokken
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            error_data = serializer.errors
            return Response(error_data, status=status.HTTP_406_NOT_ACCEPTABLE)


class UserDelete(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    renderer_classes = [UserRenderer]

    def post(self, request):
        user = request.data.get("user_id", None)
        try:
            user_exist = User.objects.get(id=user)
            if not user_exist:
                return Response({"Error": "User you want to delete not exits."},  status=status.HTTP_404_NOT_FOUND)

            user_exist.delete()

            return Response({"Success": "User deleted successfully"},  status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return Response({"Error": "May be you provide wrong user id"}, status=status.HTTP_400_BAD_REQUEST)


class UserUpdate(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        user_id = request.data.get("user_id")
        full_name = request.data.get("fullname")
        username = request.data.get("username")
        email = request.data.get("email")
        profile = request.FILES.get('file')

        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return Response({"Error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Only update fields that are provided
        if profile:
            user.profile = profile
        if full_name:
            user.full_name = full_name
        if username:
            user.username = username
        if email:
            user.email = email
        user.save()

        # Assuming you have a serializer for response
        serializer = UserUpdateserializer(user)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)



class AdminMessageView(APIView):
    """
    API view for retrieving conversations and messages between users for admin use.

    Permissions:
    - AdminUser: Only admin users can access this view.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        Retrieve conversations and messages between users for admin use.

        Returns:
        Response: List of conversations with associated messages.
        """
        conversations = {}
        sender_messages_data = {

        }
        receiver_messages_data = {
        }

        # Retrieve distinct sender-receiver pairs
        sender_receiver_pairs = Message.objects.values(
            'sender', 'receiver').distinct()

        for pair in sender_receiver_pairs:
            sender_id = pair['sender']
            receiver_id = pair['receiver']

            # Get user instances for sender and receiver
            sender = User.objects.get(pk=sender_id)
            receiver = User.objects.get(pk=receiver_id)

            # Get messages between sender and receiver
            messages = Message.objects.filter(sender=sender, receiver=receiver) | Message.objects.filter(
                sender=receiver, receiver=sender)

            # Get the minimum timestamp among the messages
            timestamp = messages.aggregate(Min('timestamp'))['timestamp__min']

            # Serialize the messages for sender and receiver separately
            sender_messages = AdminMessageSerializer(
                messages.filter(sender=sender), many=True).data
            receiver_messages = AdminMessageSerializer(
                messages.filter(sender=receiver), many=True).data
            sender_messages_data = {
                "sender_id": sender.id,
                "sender_messages": sender_messages,
            }
            receiver_messages_data = {
                "reciever_id": receiver.id,
                "reciever_messages": receiver_messages,
            }
            conversation_key = tuple(sorted([sender_id, receiver_id]))

            if conversation_key not in conversations:
                conversations[conversation_key] = {
                    "Conversation": f"Between {sender.username} and {receiver.username}",
                    "chat_data": {
                        "id": messages.first().id,  # Use the ID of the first message as the chat ID
                        # Use the order ID of the first message as the order ID
                        "order_id": messages.first().order_id,
                        "timestamp": timestamp,  # Use the minimum timestamp
                        "sender_data": sender_messages_data,
                        "receiver_data": receiver_messages_data,
                    }
                }

        # Convert the dictionary values to a list for the final response
        conversation_list = list(conversations.values())
        return Response(conversation_list)


class DeleteConversationView(APIView):
    """
    API view for deleting a specific conversation between users for admin use.

    Permissions:
    - AdminUser: Only admin users can access this view.
    """

    permission_classes = [IsAdminUser]

    def post(self, request):
        """
        Delete a specific conversation between users for admin use.

        Parameters:
        - sender_id: ID of the sender user.
        - receiver_id: ID of the receiver user.

        Returns:
        Response: Success or failure message.
        """
        sender_id = request.data.get('sender_id')
        receiver_id = request.data.get('receiver_id')

        # Ensure sender and receiver IDs are provided
        if not sender_id or not receiver_id:
            return Response({"detail": "Both sender_id and receiver_id are required."}, status=400)

        # Retrieve sender and receiver instances
        sender = get_object_or_404(User, pk=sender_id)
        receiver = get_object_or_404(User, pk=receiver_id)

        # Delete the conversation within a transaction to ensure consistency
        with transaction.atomic():
            # Delete messages between sender and receiver
            Message.objects.filter(sender=sender, receiver=receiver).delete()
            Message.objects.filter(sender=receiver, receiver=sender).delete()

        return Response({"detail": "Conversation deleted successfully."})


class SpecificChatDeletion(APIView):
    permission_classes = [IsAdminUser]
    renderer_classes = [UserRenderer]  # Make sure to import UserRenderer or remove this line if not needed

    def post(self, request):
        try:
            sender_or_receiver_id = request.data.get('person_id')

            if not sender_or_receiver_id:
                return Response({"Error": "Need sender or receiver id to delete a message."}, status=status.HTTP_400_BAD_REQUEST)

            # Get the user instance
            user = User.objects.get(id=sender_or_receiver_id)

            # Retrieve messages where the user is either the sender or the receiver
            messages_to_delete = Message.objects.filter(
                Q(sender=user) | Q(receiver=user)
            )

            # Delete the messages
            messages_to_delete.delete()

            return Response({"Success": "Messages deleted successfully"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return Response({"Error": "Sender or receiver from this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
