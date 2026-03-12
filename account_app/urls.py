# account_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('list/', views.account_list_view, name='account_list'),
    path('add/', views.add_account, name='add_account'),
    path('edit/', views.edit_account, name='edit_account'),
    path('delete/', views.delete_account, name='delete_account'),
]