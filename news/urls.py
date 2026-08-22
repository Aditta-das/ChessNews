from django.urls import path, re_path
from . import views
from django.http import HttpResponse
from django.contrib.sitemaps.views import sitemap
from .sitemaps import ArticleSitemap

def robots_txt(request):
  lines = [
      "User-agent: *",
      "Allow: /",
      "",
      "# Expressly allow major AI search bots",
      "User-agent: GPTBot",
      "Allow: /",
      "User-agent: PerplexityBot",
      "Allow: /",
      "User-agent: ClaudeBot",
      "Allow: /",
      "User-agent: Google-Extended",
      "Allow: /",
      "",
      "Sitemap: https://gmbangladesh.com/sitemap.xml",
  ]
  return HttpResponse("\n".join(lines), content_type="text/plain")


sitemaps = {
    "articles": ArticleSitemap,
}


urlpatterns = [
    path("robots.txt", robots_txt),
    path(
            "sitemap.xml",
            sitemap,
            {"sitemaps": sitemaps},
            name="django.contrib.sitemaps.views.sitemap",
        ),
    path('', views.home, name='home'),
    path('api/world-players/', views.api_world_players, name='api_world_players'),
    path('api/bd-players/', views.api_bd_players, name='api_bd_players'),
    path('api/world-women-players/', views.api_world_women_players, name='api_world_women_players'),
    path('api/bd-women-players/', views.api_bd_women_players, name='api_bd_women_players'),
    path('blogs/', views.all_blogs, name='all_blogs'),
    path('blogs/user/<str:username>/', views.user_blogs, name='user_blogs'),
    path('write-article/', views.create_article, name='write_article'),
    # Like
    re_path(
        r"^article/(?P<slug>[-\w\u0980-\u09FF]+)/like/$",
        views.toggle_like,
        name="toggle_like"
    ),

    # Edit
    re_path(
        r'^article/(?P<slug>[-\w\u0980-\u09FF]+)/edit/$',
        views.create_article,
        name='edit_article'
    ),

    # Delete
    re_path(
        r'^article/(?P<slug>[-\w\u0980-\u09FF]+)/delete/$',
        views.delete_article,
        name='delete_article'
    ),
    # DETAIL MUST BE LAST
    re_path(
        r'^article/(?P<slug>[-\w\u0980-\u09FF]+)/$',
        views.article_detail,
        name='article_detail'
    ),
    re_path(
        r'^article/(?P<slug>[-\w\u0980-\u09FF]+)/comment/add/$',
        views.add_article_comment,
        name='add_article_comment'
    ),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('reply/<int:reply_id>/delete/', views.delete_reply, name='delete_reply'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:parent_id>/reply/', views.add_article_reply, name='add_article_reply'),
    
    path('books/', views.book_list, name='book_list'),
    path('puzzles/', views.puzzle_list, name='puzzle_list'),
    path('buy-premium/', views.buy_premium, name='buy_premium'),
    path('puzzles/mark_solved/<int:puzzle_id>/', views.mark_puzzle_solved, name='mark_puzzle_solved'),
    path('trainer/find-square/', views.find_the_square, name='find_the_square'),
    path('submit-premium/', views.submit_premium_request, name='submit_premium_request'),
    # path('games/', views.games, name='games'),
    path('progress/', views.progress_profile, name='progress'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('register/', views.register_view, name='register'),
    path('forgot/',        views.forgot_step1, name='forgot_step1'),
    path('forgot/verify/', views.forgot_step2, name='forgot_step2'),
    path('forgot/reset/',  views.forgot_reset,  name='forgot_reset'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    #Trial game page
    path('games/', views.game_page, name='game_page'),
    path("upload-pgn-file/", views.upload_pgn_file, name="upload_pgn_file"),
    path('fetch-chesscom-games/', views.fetch_chesscom_games, name='fetch_chesscom_games'),
    path('save-chesscom-game/', views.save_chesscom_game, name='save_chesscom_game'),
    path('all-games/', views.all_games, name='all_games'),
    re_path(r"^game/(?P<slug>[-\w\u0980-\u09FF]+)/$", views.game_detail, name="game_detail"),
    path('game/<slug:slug>/add-comment/', views.add_comment, name='add_comment'),
    path("analyze/", views.analyze_position),
    path("search-games/", views.search_games, name="search_games"),
    path('event/', views.all_events, name='all_events'),
    path("events/", views.events_json, name="events_json"),
    path("api/events/", views.api_events_data, name="api_events_data"),
    path("api/events/bd/", views.api_bd_events_data, name="api_bd_events_data"),
    path("add-event/", views.add_event, name="add_event"),
    path("memory-test/", views.memory_view, name="memory_test"),
    path('api/memory/', views.memory_api, name='memory_api'),
    path("daily/", views.daily_puzzle_view, name="daily-puzzle"),
    path("daily/<int:daily_id>/solve/", views.submit_solve_view, name="daily-puzzle-solve"),
    ############################ Chat system ##########################################
    path("chat/", views.chat, name="chat_home"),
    path("chat/<str:username>/", views.chat, name="chat"),
    path("api/messages/<str:username>/", views.get_messages, name="get_messages"),
    path("bot", views.PlayBot, name="bot"),
    ###################################################################################
]

