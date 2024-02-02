# urls.py
from django.urls import path
from coreadmin.views import CreateUserView, UserDelete, UserUpdate,AdminMessageView, DeleteConversationView, SpecificChatDeletion

urlpatterns = [
    path('admin-users/', CreateUserView.as_view(), name='adminusercreate'),
    path('u/delete', UserDelete.as_view(), name='userdelete'),
    path('u/update', UserUpdate.as_view(), name='userupdate'),
    path('u/messages', AdminMessageView.as_view(), name='messages'),
    path('u/messages/del', DeleteConversationView.as_view(), name='delmsg'),
    path('u/messages/sp/del', SpecificChatDeletion.as_view(), name='delmsg'),
   
   
   

    # other URL patterns...
]
