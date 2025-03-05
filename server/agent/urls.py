from django.urls import path, re_path

from . import views
from . import consumers

urlpatterns = (
    path("api/conversations", views.ConversationListView.as_view()),
    path("api/conversations/<int:conversation_id>", views.ConversationView.as_view()),
    path('api/messages/<int:id>/feedback/', views.MessageFeedbackView.as_view()),
    path('api/task_status/<str:task_id>/', views.GetTaskStatus.as_view()),
    re_path(r"ws/chat/(?P<conversation_id>\d+)/", consumers.ChatConsumer.as_asgi()),

)
