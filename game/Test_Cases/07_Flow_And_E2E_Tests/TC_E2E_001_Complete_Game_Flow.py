"""
流程與端到端測試 - 完整遊戲流程
TC_E2E_001: 完整遊戲流程端到端測試
測試完整的遊戲流程：登錄 → 獲取資料 → 玩遊戲 → 查看商店 → 購買物品 → 查看成就 → 查看歷史記錄
"""
from django.test import TestCase, Client
import json
from game.models import ShopItem


class CompleteGameFlowTestCase(TestCase):
    """完整遊戲流程測試類"""

    def setUp(self):
        """測試前準備"""
        self.client = Client()
        self.username = 'testuser'

    def test_complete_game_flow(self):
        """測試用例：完整遊戲流程"""
        # 1. 登錄
        response = self.client.post(
            '/api/login/',
            data=json.dumps({'username': self.username}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # 2. 獲取初始資料
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 200)
        initial_data = json.loads(response.content)
        initial_coins = initial_data['profile']['coins']

        # 3. 玩遊戲
        response = self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 100, 'game_duration': 10.0}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        game_data = json.loads(response.content)
        self.assertEqual(game_data['coins_earned'], 100)

        # 4. 查看商店
        shop_item = ShopItem.objects.create(
            name='時間延長',
            item_type='time_extension',
            description='延長遊戲時間',
            base_price=50,
            effect_value=5.0,
            max_level=10
        )
        response = self.client.get('/api/shop/')
        self.assertEqual(response.status_code, 200)

        # 5. 購買物品
        response = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': shop_item.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # 6. 再次獲取資料驗證
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 200)
        final_data = json.loads(response.content)
        # 初始0 + 遊戲100 - 購買50 = 50
        self.assertEqual(final_data['profile']['coins'], 50)
        self.assertEqual(final_data['profile']['total_games_played'], 1)

        # 7. 查看成就
        response = self.client.get('/api/achievements/')
        self.assertEqual(response.status_code, 200)

        # 8. 查看歷史記錄
        response = self.client.get('/api/history/')
        self.assertEqual(response.status_code, 200)
        history_data = json.loads(response.content)
        self.assertEqual(len(history_data['history']), 1)

