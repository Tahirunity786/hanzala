from django.urls import path
from payments.views import PaymentView

urlpatterns = [
    path("public/payment/processing", PaymentView.as_view(), name="pyment")
]
