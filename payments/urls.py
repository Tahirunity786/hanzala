from django.urls import path
from payments.views import PaymentAPI

urlpatterns = [
    path("public/payment/processing", PaymentAPI.as_view(), name="pyment")
]
