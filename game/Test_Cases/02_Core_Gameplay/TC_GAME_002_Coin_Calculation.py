"""
核心遊戲玩法測試 - 金幣計算
TC_GAME_002: 金幣計算邏輯測試（包含延長時間模式）
"""
from django.test import TestCase, Client
import json


class CoinCalculationTestCase(TestCase):
    """金幣計算測試類"""

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

    def test_submit_game_with_extended_time(self):
        """測試用例：提交延長時間的遊戲結果"""
        # 提交延長時間的遊戲結果（15秒，100次點擊）
        clicks = 100
        game_duration = 15.0
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
        # 前10秒點擊：100 * (10/15) = 66.67 -> 66次，每次1金幣
        # 後5秒點擊：100 - 66 = 34次，每次2金幣
        # 總金幣：66 + 34*2 = 134
        expected_coins = int(clicks * (10.0 / game_duration)) + (clicks - int(clicks * (10.0 / game_duration))) * 2
        self.assertEqual(data['coins_earned'], expected_coins)

