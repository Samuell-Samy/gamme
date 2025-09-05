from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),
    path('login/', views.login_page, name='login'),
    # Health check endpoint
    path('health/', views.health_check, name='health_check'),
    # Legacy support for direct .html routes
    path('login.html', views.login_page),
    path('index.html', views.index),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path('admin_panel/games/new/', views.admin_game_create, name='admin_game_create'),
    path('admin_panel/games/<int:game_id>/', views.admin_game_detail, name='admin_game_detail'),
    # API endpoints
    path('api/folders/', views.api_folders, name='api_folders'),
    path('api/folders/<int:folder_id>/games/', views.api_folder_games, name='api_folder_games'),
    path('api/games/', views.api_games, name='api_games'),
    path('api/games/<int:game_id>/', views.api_game_detail, name='api_game_detail'),
    path('api/search/', views.api_search_games, name='api_search_games'),
    # Public API endpoints (no authentication required)
    path('api/public/folders/<int:folder_id>/games/', views.api_public_folder_games, name='api_public_folder_games'),
    path('api/public/search/', views.api_public_search_games, name='api_public_search_games'),
]
