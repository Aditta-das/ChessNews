from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blogs/', views.all_blogs, name='all_blogs'),
    path('write-article/', views.create_article, name='write_article'),
    re_path(r"^article/(?P<slug>[-\w\u0980-\u09FF]+)/$", views.article_detail, name="article_detail"),
    path('books/', views.book_list, name='book_list'),
    path('puzzles/', views.puzzle_list, name='puzzle_list'),
    path('buy-premium/', views.buy_premium, name='buy_premium'),
    path('puzzles/mark_solved/<int:puzzle_id>/', views.mark_puzzle_solved, name='mark_puzzle_solved'),
    path('trainer/find-square/', views.find_the_square, name='find_the_square'),
    path('submit-premium/', views.submit_premium_request, name='submit_premium_request'),
    path('games/', views.games, name='games'),
    path('progress/', views.progress_profile, name='progress'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
