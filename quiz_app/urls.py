from django.urls import path
from . import views

urlpatterns = [
    path('subjects/', views.subject_list_view, name='subject_list'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('subjects/delete/<int:subject_id>/', views.delete_subject, name='delete_subject'),

    path('subjects/<int:subject_id>/quizzes/', views.quiz_list_view, name='quiz_list'),
    path('subjects/<int:subject_id>/quizzes/create/', views.create_quiz_view, name='create_quiz'),
    path('quizzes/<int:quiz_id>/edit/', views.edit_quiz_view, name='edit_quiz'),
    path('quizzes/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),

    path('exam/<int:quiz_id>/', views.exam_view, name='exam'),
    path('result/<int:result_id>/', views.result_view, name='result'),
    path('result/<int:result_id>/review/', views.review_view, name='review_quiz'),

    path('home/', views.home_view, name='home'),
    path('history/', views.history_view, name='history'),
    path('search/', views.search_view, name='search'),
]