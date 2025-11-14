from django.contrib import admin
from .models import (
    PlayerProfile, GameSession, ShopItem, 
    PlayerPurchase, Achievement, PlayerAchievement
)


@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'coins', 'total_clicks', 'best_clicks_per_round', 'total_games_played']
    search_fields = ['user__username']
    list_filter = ['created_at']


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'clicks', 'game_duration', 'coins_earned', 'played_at']
    list_filter = ['played_at']
    search_fields = ['user__username']
    date_hierarchy = 'played_at'


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'item_type', 'base_price', 'effect_value', 'max_level']
    list_filter = ['item_type']


@admin.register(PlayerPurchase)
class PlayerPurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'shop_item', 'level', 'price_paid', 'purchased_at']
    list_filter = ['shop_item', 'purchased_at']
    search_fields = ['user__username']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'achievement_type', 'target_value', 'reward_coins', 'icon']
    list_filter = ['achievement_type']


@admin.register(PlayerAchievement)
class PlayerAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'unlocked_at', 'reward_claimed']
    list_filter = ['unlocked_at', 'reward_claimed']
    search_fields = ['user__username']
