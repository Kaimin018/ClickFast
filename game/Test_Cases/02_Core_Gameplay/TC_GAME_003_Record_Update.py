"""
核心遊戲玩法測試 - 記錄更新
TC_GAME_003: 最佳點擊記錄更新邏輯測試
"""
from django.test import TestCase, Client
import json
from game.models import PlayerProfile


class RecordUpdateTestCase(TestCase):
    """記錄更新測試類"""

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

    def test_update_best_clicks_record(self):
        """測試用例：更新最佳點擊記錄"""
        # 第一次遊戲：50次點擊
        response1 = self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 50, 'game_duration': 10.0}),
            content_type='application/json'
        )
        data1 = json.loads(response1.content)
        self.assertEqual(data1['profile']['best_clicks_per_round'], 50)

        # 第二次遊戲：30次點擊（不應該更新最佳記錄）
        response2 = self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 30, 'game_duration': 10.0}),
            content_type='application/json'
        )
        data2 = json.loads(response2.content)
        self.assertEqual(data2['profile']['best_clicks_per_round'], 50)

        # 第三次遊戲：80次點擊（應該更新最佳記錄）
        response3 = self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 80, 'game_duration': 10.0}),
            content_type='application/json'
        )
        data3 = json.loads(response3.content)
        self.assertEqual(data3['profile']['best_clicks_per_round'], 80)

        # 驗證資料庫
        profile = PlayerProfile.objects.get(user__username=self.username)
        self.assertEqual(profile.best_clicks_per_round, 80)

