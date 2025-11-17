"""
成就系統測試 - 成就列表
TC_ACH_001: 成就列表查詢測試
"""
from django.test import TestCase, Client
import json
from game.models import Achievement, PlayerAchievement, PlayerProfile
from django.contrib.auth.models import User


class AchievementListTestCase(TestCase):
    """成就列表測試類"""

    def setUp(self):
        """測試前準備"""
        self.client = Client()
        self.username = 'testuser'
        # 先登錄
        self.client.post(
            '/api/login/',
            data=json.dumps({'username': self.username}),
            content_type='application/json'
        )

    def test_get_achievements(self):
        """測試用例：獲取成就列表"""
        # 獲取測試用戶
        user = User.objects.get(username=self.username)
        
        # 確保用戶有 profile，並重置 total_clicks 為 0
        profile, _ = PlayerProfile.objects.get_or_create(
            user=user,
            defaults={'coins': 0, 'total_clicks': 0, 'best_clicks_per_round': 0, 'total_games_played': 0, 'battle_wins': 0}
        )
        # 確保 total_clicks 為 0，不會觸發成就解鎖
        profile.total_clicks = 0
        profile.save()
        
        # 創建測試成就（使用較高的目標值，確保不會被自動解鎖）
        # 使用唯一的名稱和時間戳，避免與其他測試衝突
        import time
        unique_name = f'測試成就_{int(time.time() * 1000)}'
        achievement = Achievement.objects.create(
            name=unique_name,
            description='測試用成就',
            achievement_type='total_clicks',
            target_value=999999,  # 使用極高的目標值，確保測試用戶不會解鎖
            reward_coins=10,
            icon='🎯'
        )
        
        # 確保測試用戶沒有解鎖這個成就（刪除可能存在的解鎖記錄）
        # 同時刪除所有可能存在的 PlayerAchievement 記錄，確保測試乾淨
        PlayerAchievement.objects.filter(user=user, achievement=achievement).delete()
        
        # 驗證確實沒有解鎖記錄
        unlocked_count = PlayerAchievement.objects.filter(user=user, achievement=achievement).count()
        self.assertEqual(unlocked_count, 0, f"應該沒有解鎖記錄，但發現 {unlocked_count} 條記錄")

        # 獲取成就列表
        response = self.client.get('/api/achievements/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('achievements', data)
        self.assertGreater(len(data['achievements']), 0)
        
        # 查找測試創建的成就（不假設它是第一個）
        test_achievement = None
        for ach in data['achievements']:
            if ach['name'] == achievement.name:
                test_achievement = ach
                break
        
        # 確認找到了測試創建的成就
        self.assertIsNotNone(test_achievement, "找不到測試創建的成就")
        self.assertEqual(test_achievement['name'], achievement.name)
        self.assertEqual(test_achievement['description'], achievement.description)
        # 驗證成就未解鎖（total_clicks=0 < 999999）
        self.assertFalse(test_achievement['unlocked'], f"成就應該未解鎖，但顯示為已解鎖。用戶 total_clicks: {profile.total_clicks}")

        # 測試未登錄狀態
        client2 = Client()
        response2 = client2.get('/api/achievements/')
        self.assertEqual(response2.status_code, 401)

