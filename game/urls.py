from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/login/', views.api_login_or_register, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/profile/', views.api_get_profile, name='api_profile'),
    path('api/submit-game/', views.api_submit_game, name='api_submit_game'),
    path('api/shop/', views.api_get_shop, name='api_shop'),
    path('api/purchase/', views.api_purchase_item, name='api_purchase'),
    path('api/achievements/', views.api_get_achievements, name='api_achievements'),
    path('api/history/', views.api_get_game_history, name='api_history'),
    path('api/update-badges/', views.api_update_badges, name='api_update_badges'),
    path('api/rollback-shop-level/', views.api_rollback_shop_level, name='api_rollback_shop_level'),
    path('api/rollback-all-shop-items/', views.api_rollback_all_shop_items, name='api_rollback_all_shop_items'),
]
