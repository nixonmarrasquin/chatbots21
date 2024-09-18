"""
URL configuration for chatbot_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from chatbot import views as chatbot_views  # Importa las vistas de la app chatbot

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', chatbot_views.chatbot_page, name='home'),  # Define la ruta para la página principal
    path('chatbot/', include('chatbot.urls')),  # Mantén la ruta del chatbot
    path('dashboard/', chatbot_views.dashboard_page, name='dashboard'),

]