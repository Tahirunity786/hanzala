import datetime
import os
from django.conf import settings
from firebase_admin import credentials, initialize_app
from fcm_django.models import FCMDevice
from firebase_admin import messaging 

# Define the path to the Firebase Admin SDK credentials file
credential_path = os.path.join(settings.BASE_DIR, "credential.json")

# Initialize Firebase Admin SDK with the credentials
cred = credentials.Certificate(credential_path)

initialize_app(cred)

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
    response = False  # Initialize response variable outside the try block
    try:
        # Create an FCM message with the provided title, body, and target token
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
            android=messaging.AndroidConfig(
                ttl=datetime.timedelta(seconds=3600),
                priority='high',
                notification=messaging.AndroidNotification(
                    icon='stock_ticker_update',
                    color='#f45342'
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(badge=42),
                ),
            ),
        )
        

        messaging.send(message)
        return True
    except Exception as e:
        return response
