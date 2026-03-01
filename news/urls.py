from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blogs/', views.all_blogs, name='all_blogs'),
    path('blogs/user/<str:username>/', views.user_blogs, name='user_blogs'),
    path('write-article/', views.create_article, name='write_article'),
    re_path(r'^article/(?P<slug>[-\w\u0980-\u09FF]+)/edit/$', views.create_article, name='edit_article'),
    re_path(r'^article/(?P<slug>[-\w\u0980-\u09FF]+)/delete/$', views.delete_article, name='delete_article'),
    re_path(r'^article/(?P<slug>[-\w\u0980-\u09FF]+)/$', views.article_detail, name='article_detail'),
    re_path(r"^article/(?P<slug>[-\w\u0980-\u09FF]+)/like/$", views.toggle_like, name="toggle_like"),
    path('books/', views.book_list, name='book_list'),
    path('puzzles/', views.puzzle_list, name='puzzle_list'),
    path('buy-premium/', views.buy_premium, name='buy_premium'),
    path('puzzles/mark_solved/<int:puzzle_id>/', views.mark_puzzle_solved, name='mark_puzzle_solved'),
    path('trainer/find-square/', views.find_the_square, name='find_the_square'),
    path('submit-premium/', views.submit_premium_request, name='submit_premium_request'),
    # path('games/', views.games, name='games'),
    path('progress/', views.progress_profile, name='progress'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    #Trial game page
    path('games/', views.game_page, name='game_page'),
    path('fetch-chesscom-games/', views.fetch_chesscom_games, name='fetch_chesscom_games'),
    path('save-chesscom-game/', views.save_chesscom_game, name='save_chesscom_game'),
    path('all-games/', views.all_games, name='all_games'),
    re_path(r"^game/(?P<slug>[-\w\u0980-\u09FF]+)/$", views.game_detail, name="game_detail"),
    path('game/<slug:slug>/add-comment/', views.add_comment, name='add_comment'),
    path("analyze/", views.analyze_position),
    path("search-games/", views.search_games, name="search_games"),
    path('event/', views.all_events, name='all_events'),
    path("events/", views.events_json, name="events_json"),
    path("add-event/", views.add_event, name="add_event"),

]

