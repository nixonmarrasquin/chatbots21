from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chatbot, name='chatbot'),
     path('', views.chatbot_page, name='chatbot_page'),
]
