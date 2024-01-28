import os
from django.conf import settings
from firebase_admin import credentials
import firebase_admin

# Define the path to the Firebase Admin SDK credentials file
credential_path = os.path.join(settings.BASE_DIR, "hanzala-ab5c5-firebase-adminsdk-rg84h-7490b8f388.json")

# Initialize Firebase Admin SDK with the credentials
cred = credentials.Certificate(credential_path)
firebase_admin.initialize_app(cred)

from firebase_admin import messaging

def send_message(token, body, title) -> bool:
    """
    Sends a Firebase Cloud Messaging (FCM) message.

    Parameters:
    - token (str): The device token to which the message will be sent.
    - body (str): The body of the FCM message.
    - title (str): The title of the FCM message.

    Returns:
    - bool: True if the message was sent successfully, False otherwise.
    """

    # Create an FCM message with the provided title, body, and target token
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )

    try:
        # Send the FCM message
        messaging.send(message)
        return True
    except Exception as e:
        # Handle any exceptions that might occur during message sending
        # You might want to log the error or perform additional actions based on your requirements
        print(f"Error sending FCM message: {e}")
        return False

