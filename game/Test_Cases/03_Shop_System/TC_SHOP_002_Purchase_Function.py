"""
商店系統測試 - 購買功能
TC_SHOP_002: 購買功能和價格計算測試
"""
from django.test import TestCase, Client
import json
from game.models import ShopItem, PlayerProfile, PlayerPurchase


class PurchaseFunctionTestCase(TestCase):
    """購買功能測試類"""

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

    def test_purchase_shop_item(self):
        """測試用例：購買商店物品"""
        # 創建商店物品
        shop_item = ShopItem.objects.create(
            name='時間延長',
            item_type='time_extension',
            description='延長遊戲時間',
            base_price=100,
            effect_value=5.0,
            max_level=10
        )

        # 先玩遊戲獲得金幣
        self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 150, 'game_duration': 10.0}),
            content_type='application/json'
        )

        # 購買物品
        response = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': shop_item.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['new_level'], 1)
        self.assertEqual(data['coins_remaining'], 50)  # 150 - 100 = 50

        # 驗證購買記錄
        purchase = PlayerPurchase.objects.filter(
            user__username=self.username,
            shop_item=shop_item
        ).first()
        self.assertIsNotNone(purchase)
        self.assertEqual(purchase.level, 1)

        # 驗證玩家金幣減少
        profile = PlayerProfile.objects.get(user__username=self.username)
        self.assertEqual(profile.coins, 50)

        # 測試金幣不足
        response2 = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': shop_item.id}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 400)

        # 測試未登錄狀態
        client2 = Client()
        response3 = client2.post(
            '/api/purchase/',
            data=json.dumps({'item_id': shop_item.id}),
            content_type='application/json'
        )
        self.assertEqual(response3.status_code, 401)

    def test_purchase_multiple_levels(self):
        """測試用例：購買多個等級的物品"""
        # 創建商店物品
        shop_item = ShopItem.objects.create(
            name='自動點擊器',
            item_type='auto_clicker',
            description='自動點擊',
            base_price=100,
            effect_value=1.0,
            max_level=5
        )

        # 獲得足夠金幣（100 + 200 + 300 + 400 = 1000）
        self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 1000, 'game_duration': 10.0}),
            content_type='application/json'
        )

        # 購買等級1（價格：100 * 1 = 100）
        response1 = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': shop_item.id}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 200)
        data1 = json.loads(response1.content)
        self.assertEqual(data1['new_level'], 1)

        # 購買等級2（價格：100 * 2 = 200）
        response2 = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': shop_item.id}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.content)
        self.assertEqual(data2['new_level'], 2)

        # 驗證購買記錄
        purchase = PlayerPurchase.objects.get(
            user__username=self.username,
            shop_item=shop_item
        )
        self.assertEqual(purchase.level, 2)

        # 驗證剩餘金幣（1000 - 100 - 200 = 700）
        profile = PlayerProfile.objects.get(user__username=self.username)
        self.assertEqual(profile.coins, 700)

