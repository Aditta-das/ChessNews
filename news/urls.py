from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('books/', views.book_list, name='book_list'),
    path('puzzles/', views.puzzle_list, name='puzzle_list'),
    path('puzzles/mark_solved/<int:puzzle_id>/', views.mark_puzzle_solved, name='mark_puzzle_solved'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
