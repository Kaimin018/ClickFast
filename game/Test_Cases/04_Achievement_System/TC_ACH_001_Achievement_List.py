"""
成就系統測試 - 成就列表
TC_ACH_001: 成就列表查詢測試
"""
from django.test import TestCase, Client
import json
from game.models import Achievement


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
        # 創建測試成就
        achievement = Achievement.objects.create(
            name='首次點擊',
            description='完成第一次點擊',
            achievement_type='single_round',
            target_value=1,
            reward_coins=10,
            icon='🎯'
        )

        # 獲取成就列表
        response = self.client.get('/api/achievements/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('achievements', data)
        self.assertGreater(len(data['achievements']), 0)
        ach = data['achievements'][0]
        self.assertEqual(ach['name'], achievement.name)
        self.assertFalse(ach['unlocked'])  # 尚未解鎖

        # 測試未登錄狀態
        client2 = Client()
        response2 = client2.get('/api/achievements/')
        self.assertEqual(response2.status_code, 401)

