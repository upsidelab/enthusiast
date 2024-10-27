from django.urls import path

from . import views

urlpatterns = [
    path('api/ask/', views.GetAnswer.as_view(), name='get_answer'),
    path('api/task_status/<str:task_id>/', views.GetTaskStatus.as_view()),
    path("api/conversations/<int:data_set_id>", views.ConversationListView.as_view()),
]