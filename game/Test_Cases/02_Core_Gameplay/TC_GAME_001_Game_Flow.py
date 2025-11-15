"""
核心遊戲玩法測試 - 遊戲流程
TC_GAME_001: 遊戲基本流程和結果提交測試
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
import json
from game.models import PlayerProfile, GameSession


class GameFlowTestCase(TestCase):
    """遊戲流程測試類"""

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

    def test_get_user_profile(self):
        """測試用例：獲取用戶資料"""
        # 獲取資料
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('profile', data)
        self.assertIn('purchases', data)
        self.assertIn('achievements', data)
        self.assertEqual(data['profile']['coins'], 0)

        # 測試未登錄狀態
        client2 = Client()
        response2 = client2.get('/api/profile/')
        self.assertEqual(response2.status_code, 401)

    def test_submit_game_result(self):
        """測試用例：提交遊戲結果"""
        # 提交遊戲結果
        clicks = 50
        game_duration = 10.0
        response = self.client.post(
            '/api/submit-game/',
            data=json.dumps({
                'clicks': clicks,
                'game_duration': game_duration
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['coins_earned'], clicks)  # 10秒內每次點擊1金幣
        self.assertEqual(data['profile']['total_clicks'], clicks)
        self.assertEqual(data['profile']['total_games_played'], 1)
        self.assertEqual(data['profile']['best_clicks_per_round'], clicks)

        # 驗證資料庫記錄
        profile = PlayerProfile.objects.get(user__username=self.username)
        self.assertEqual(profile.coins, clicks)
        self.assertEqual(profile.total_clicks, clicks)
        self.assertEqual(profile.total_games_played, 1)

        # 驗證遊戲記錄
        session = GameSession.objects.filter(user__username=self.username).first()
        self.assertIsNotNone(session)
        self.assertEqual(session.clicks, clicks)
        self.assertEqual(session.game_duration, game_duration)

        # 測試未登錄狀態
        client2 = Client()
        response2 = client2.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 10, 'game_duration': 10.0}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 401)

