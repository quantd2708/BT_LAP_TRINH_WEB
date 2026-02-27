"""
URL configuration for quizzz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from account_app import views
from quiz_app import views as quiz_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
     path('accounts/', views.account_list_view, name='account_list'),
    path('history/', quiz_views.history_view, name='history'),
    path('home/', quiz_views.home_view, name='home'),
    path('subjects/', quiz_views.subject_list_view, name='subject_list'),
    path('quizzes/', quiz_views.quiz_list_view, name='quiz_list'),
    path('create-quiz/', quiz_views.create_quiz_view, name='create_quiz'),
    path('exam/<int:quiz_id>/', quiz_views.exam_view, name='exam'),
    path('result/<int:quiz_id>/', quiz_views.result_view, name='result'),
    path('search/', quiz_views.search_view, name='search'),
]
