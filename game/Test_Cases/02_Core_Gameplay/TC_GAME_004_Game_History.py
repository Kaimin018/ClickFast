"""
核心遊戲玩法測試 - 遊戲歷史記錄
TC_GAME_004: 遊戲歷史記錄查詢測試
"""
from django.test import TestCase, Client
import json


class GameHistoryTestCase(TestCase):
    """遊戲歷史記錄測試類"""

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

    def test_get_game_history(self):
        """測試用例：獲取遊戲歷史記錄"""
        # 提交多個遊戲結果
        for i in range(3):
            self.client.post(
                '/api/submit-game/',
                data=json.dumps({
                    'clicks': 20 + i * 10,
                    'game_duration': 10.0
                }),
                content_type='application/json'
            )

        # 獲取歷史記錄
        response = self.client.get('/api/history/?limit=10')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('history', data)
        self.assertEqual(len(data['history']), 3)

        # 驗證記錄順序（最新的在前）
        self.assertEqual(data['history'][0]['clicks'], 40)
        self.assertEqual(data['history'][1]['clicks'], 30)
        self.assertEqual(data['history'][2]['clicks'], 20)

        # 測試限制數量
        response2 = self.client.get('/api/history/?limit=2')
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.content)
        self.assertEqual(len(data2['history']), 2)

        # 測試未登錄狀態
        client2 = Client()
        response3 = client2.get('/api/history/')
        self.assertEqual(response3.status_code, 401)

