from django.urls import path, include
from django.contrib import admin
from backend import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # REST Framework auth (browsable API)
    path('api-auth/', include('rest_framework.urls')),

    # GameTrack API endpoints
    path('api/players/search', views.lookup_player, name='lookup-player'),
    path('api/players/<str:puuid>/matches', views.get_player_matches, name='player-matches'),

    # Fetch stats using get_stats functions (user input from frontend)
    path('api/players/fetch-stats', views.fetch_player_stats, name='fetch-player-stats'),

    # Cached data endpoint (reads from JSON files created by main.py)
    path('api/matches/cached', views.get_cached_matches, name='cached-matches'),
]
