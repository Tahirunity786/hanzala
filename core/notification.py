import os
from django.conf import settings
from firebase_admin import credentials
import firebase_admin
credential_path = os.path.join(settings.BASE_DIR, "hanzala-ab5c5-firebase-adminsdk-rg84h-7490b8f388.json")
cred = credentials.Certificate(credential_path)
firebase_admin.initialize_app(cred)


from firebase_admin import messaging

def send_message(token,body,title)->bool:
    # Create an FCM message with the provided title, body, and target token
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )
    # Send the FCM message
    messaging.send(message)
    return True

