from django.urls import path
from payments.views import PaymentView, PaymentDetail

urlpatterns = [
    path("public/payment/processing", PaymentView.as_view(), name="payment"),
    path("public/payment/consumer", PaymentDetail.as_view(), name="payment-consumer"),
   
]
