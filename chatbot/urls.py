from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chatbot, name='chatbot'),
    path('', views.chatbot_page, name='chatbot_page'),
    path('dashboard/', views.dashboard_page, name='dashboard'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),  # Nueva ruta
    
]
