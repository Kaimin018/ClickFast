from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class PlayerProfile(models.Model):
    """玩家資料，存儲貨幣和遊戲數據"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    coins = models.BigIntegerField(default=0, verbose_name="金幣")
    total_clicks = models.BigIntegerField(default=0, verbose_name="總點擊次數")
    best_clicks_per_round = models.IntegerField(default=0, verbose_name="單局最佳點擊次數")
    total_games_played = models.IntegerField(default=0, verbose_name="總遊戲局數")
    battle_wins = models.IntegerField(default=0, verbose_name="對戰勝場數")
    # 用戶選擇的三個成就徽章ID（用於右上角顯示）
    badge_1_id = models.IntegerField(null=True, blank=True, verbose_name="徽章1")
    badge_2_id = models.IntegerField(null=True, blank=True, verbose_name="徽章2")
    badge_3_id = models.IntegerField(null=True, blank=True, verbose_name="徽章3")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.coins} 金幣"

    class Meta:
        verbose_name = "玩家資料"
        verbose_name_plural = "玩家資料"


class GameSession(models.Model):
    """遊戲會話記錄"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_sessions')
    clicks = models.IntegerField(default=0, verbose_name="點擊次數")
    game_duration = models.FloatField(default=10.0, verbose_name="遊戲時長（秒）")
    coins_earned = models.IntegerField(default=0, verbose_name="獲得金幣")
    played_at = models.DateTimeField(auto_now_add=True, verbose_name="遊戲時間")

    def __str__(self):
        return f"{self.user.username} - {self.clicks} 點擊 - {self.played_at}"

    class Meta:
        verbose_name = "遊戲記錄"
        verbose_name_plural = "遊戲記錄"
        ordering = ['-played_at']


class ShopItem(models.Model):
    """商店物品"""
    ITEM_TYPES = [
        ('time_extension', '遊戲時間延長'),
        ('extra_button', '額外點擊按鈕'),
        ('auto_clicker', '自動點擊器'),
    ]

    name = models.CharField(max_length=100, verbose_name="物品名稱")
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, verbose_name="物品類型")
    description = models.TextField(verbose_name="描述")
    base_price = models.IntegerField(verbose_name="基礎價格")
    effect_value = models.FloatField(default=0, verbose_name="效果值")
    # 對於時間延長：effect_value = 每次升級增加的秒數
    # 對於額外按鈕：effect_value = 每次升級增加的按鈕數量
    # 對於自動點擊器：effect_value 不再使用，頻率由等級直接計算（Lv.1=3秒/次，Lv.2=2秒/次，Lv.3=1秒/次，Lv.4+=每秒(等級-2)次）
    max_level = models.IntegerField(default=10, verbose_name="最大等級")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_item_type_display()})"

    class Meta:
        verbose_name = "商店物品"
        verbose_name_plural = "商店物品"


class PlayerPurchase(models.Model):
    """玩家購買記錄"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    shop_item = models.ForeignKey(ShopItem, on_delete=models.CASCADE, related_name='purchases')
    level = models.IntegerField(default=1, verbose_name="等級")
    price_paid = models.IntegerField(verbose_name="支付價格")
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name="購買時間")

    def __str__(self):
        return f"{self.user.username} - {self.shop_item.name} Lv.{self.level}"

    class Meta:
        verbose_name = "購買記錄"
        verbose_name_plural = "購買記錄"
        unique_together = ['user', 'shop_item']  # 每個用戶每種物品只能有一條記錄


class Achievement(models.Model):
    """成就定義"""
    name = models.CharField(max_length=100, verbose_name="成就名稱")
    description = models.TextField(verbose_name="成就描述")
    achievement_type = models.CharField(max_length=50, verbose_name="成就類型")
    # 例如: 'total_clicks_1000', 'single_round_100', 'total_games_50'
    target_value = models.BigIntegerField(verbose_name="目標值")
    reward_coins = models.IntegerField(default=0, verbose_name="獎勵金幣")
    icon = models.CharField(max_length=50, default="🏆", verbose_name="圖標")

    def __str__(self):
        return f"{self.name} - {self.target_value}"

    class Meta:
        verbose_name = "成就"
        verbose_name_plural = "成就"


class PlayerAchievement(models.Model):
    """玩家成就解鎖記錄"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='player_achievements')
    unlocked_at = models.DateTimeField(auto_now_add=True, verbose_name="解鎖時間")
    reward_claimed = models.BooleanField(default=False, verbose_name="獎勵已領取")

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

    class Meta:
        verbose_name = "玩家成就"
        verbose_name_plural = "玩家成就"
        unique_together = ['user', 'achievement']
