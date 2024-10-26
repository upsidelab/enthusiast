from django.urls import path

from . import views

urlpatterns = [
    path('api/ask/', views.GetAnswer.as_view(), name='get_answer'),
    path("api/conversations/<int:data_set_id>", views.ConversationListView.as_view()),
]