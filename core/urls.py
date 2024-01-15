from django.urls import path
from core.views import CreateUser
urlpatterns = [
    path('public/u/create', CreateUser.as_view(), name="Usercreation")
]
