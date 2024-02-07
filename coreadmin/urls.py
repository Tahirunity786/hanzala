# urls.py
from django.urls import path
from coreadmin.views import CreateUserView, OrderList, PaymentModifierCreateView, UserDelete, UserUpdate,AdminMessageView, DeleteConversationView, SpecificChatDeletion,DeleteProductByAdminView, BlockUserView, UnblockUserView,ListUsersView,PaymentDetail

urlpatterns = [
    path('admin-users/', CreateUserView.as_view(), name='adminusercreate'),
    path('orders/details', OrderList.as_view(), name='order-list'),
    path('product/delete', DeleteProductByAdminView.as_view(), name='product-delete'),
    path('users/', ListUsersView.as_view(), name='list_users'),
    path('u/delete', UserDelete.as_view(), name='userdelete'),
    path('u/update', UserUpdate.as_view(), name='userupdate'),
    path('u/messages', AdminMessageView.as_view(), name='messages'),
    path('u/messages/del', DeleteConversationView.as_view(), name='delmsg'),
    path('u/messages/sp/del', SpecificChatDeletion.as_view(), name='delmsg'),
    path('users/block/', BlockUserView.as_view(), name='block_user'),
    path('users/unblock/', UnblockUserView.as_view(), name='unblock_user'),
    path('admin-users/payment_modifier', PaymentModifierCreateView.as_view(), name='payment_modifier_create'),
    path("public/payment/details", PaymentDetail.as_view(), name="payment-consumer"),
   
   
   

    # other URL patterns...
]
