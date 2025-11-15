"""
成就系統測試 - 成就解鎖
TC_ACH_002: 成就解鎖機制和獎勵發放測試
"""
from django.test import TestCase, Client
import json
from game.models import Achievement, PlayerProfile, PlayerAchievement


class AchievementUnlockTestCase(TestCase):
    """成就解鎖測試類"""

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

    def test_achievement_unlock(self):
        """測試用例：成就解鎖"""
        # 創建測試成就
        achievement = Achievement.objects.create(
            name='點擊達人',
            description='單局點擊達到50次',
            achievement_type='single_round',
            target_value=50,
            reward_coins=100,
            icon='🏆'
        )

        # 提交達到成就目標的遊戲結果
        response = self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 50, 'game_duration': 10.0}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # 應該解鎖成就
        self.assertGreater(len(data['new_achievements']), 0)
        self.assertEqual(data['new_achievements'][0]['name'], achievement.name)

        # 驗證成就記錄
        player_achievement = PlayerAchievement.objects.filter(
            user__username=self.username,
            achievement=achievement
        ).first()
        self.assertIsNotNone(player_achievement)
        self.assertTrue(player_achievement.reward_claimed)

        # 驗證獎勵金幣已發放
        profile = PlayerProfile.objects.get(user__username=self.username)
        # 50次點擊 = 50金幣 + 成就獎勵100金幣 = 150金幣
        self.assertEqual(profile.coins, 150)

