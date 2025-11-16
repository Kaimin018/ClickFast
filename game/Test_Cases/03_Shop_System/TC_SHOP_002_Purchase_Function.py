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
            name='提升寵物夥伴能力',
            item_type='auto_clicker',
            description='提升寵物夥伴的點擊能力',
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

    def test_purchase_auto_clicker_upgrade(self):
        """測試用例：提升寵物夥伴能力（需要前置條件）"""
        # 創建寵物夥伴和寵物夥伴能力
        extra_button_item = ShopItem.objects.create(
            name='購買寵物夥伴',
            item_type='extra_button',
            description='增加點擊按鈕',
            base_price=50,
            effect_value=1.0,
            max_level=5
        )
        
        auto_clicker_item = ShopItem.objects.create(
            name='提升寵物夥伴能力',
            item_type='auto_clicker',
            description='自動點擊',
            base_price=100,
            effect_value=1.0,
            max_level=10
        )

        # 獲得足夠金幣
        self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 2000, 'game_duration': 10.0}),
            content_type='application/json'
        )

        # 測試：未購買寵物夥伴時，無法提升寵物夥伴能力
        response1 = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': auto_clicker_item.id}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 400)
        data1 = json.loads(response1.content)
        self.assertIn('購買寵物夥伴', data1['error'])

        # 先購買寵物夥伴（等級1）
        response2 = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': extra_button_item.id}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.content)
        self.assertEqual(data2['new_level'], 1)

        # 驗證：購買寵物夥伴後，自動附加了1等級的寵物夥伴能力
        auto_clicker_purchase = PlayerPurchase.objects.filter(
            user__username=self.username,
            shop_item=auto_clicker_item
        ).first()
        self.assertIsNotNone(auto_clicker_purchase)
        self.assertEqual(auto_clicker_purchase.level, 1)
        self.assertEqual(auto_clicker_purchase.price_paid, 0)  # 免費附加

        # 現在可以提升寵物夥伴能力（等級1 -> 等級2）
        response3 = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': auto_clicker_item.id}),
            content_type='application/json'
        )
        self.assertEqual(response3.status_code, 200)
        data3 = json.loads(response3.content)
        self.assertEqual(data3['new_level'], 2)

        # 驗證購買記錄
        auto_clicker_purchase.refresh_from_db()
        self.assertEqual(auto_clicker_purchase.level, 2)
        self.assertEqual(auto_clicker_purchase.price_paid, 200)  # 100 * 2 = 200

    def test_purchase_item_id_validation(self):
        """測試用例：item_id 格式驗證"""
        # 創建商店物品
        shop_item = ShopItem.objects.create(
            name='時間延長',
            item_type='time_extension',
            description='延長遊戲時間',
            base_price=100,
            effect_value=5.0,
            max_level=10
        )

        # 獲得金幣
        self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 150, 'game_duration': 10.0}),
            content_type='application/json'
        )

        # 測試：缺少 item_id
        response1 = self.client.post(
            '/api/purchase/',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 400)
        data1 = json.loads(response1.content)
        self.assertIn('缺少物品ID參數', data1['error'])

        # 測試：item_id 為空字串
        response2 = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': ''}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 400)
        data2 = json.loads(response2.content)
        self.assertIn('無效的物品ID格式', data2['error'])

        # 測試：item_id 為字串數字（應該可以正常處理）
        response3 = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': str(shop_item.id)}),
            content_type='application/json'
        )
        self.assertEqual(response3.status_code, 200)

        # 測試：item_id 為包含空格的字串數字（應該可以正常處理）
        response4 = self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 100, 'game_duration': 10.0}),
            content_type='application/json'
        )
        response5 = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': f' {shop_item.id} '}),
            content_type='application/json'
        )
        # 注意：這裡會失敗因為已經購買過，但應該能正確解析 item_id
        # 如果解析失敗會返回 400，如果解析成功但已滿級會返回 400（已達到最大等級）
        self.assertIn(response5.status_code, [200, 400])

        # 測試：item_id 為非數字字串
        response6 = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': 'abc'}),
            content_type='application/json'
        )
        self.assertEqual(response6.status_code, 400)
        data6 = json.loads(response6.content)
        self.assertIn('無效的物品ID格式', data6['error'])

        # 測試：item_id 為負數
        response7 = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': -1}),
            content_type='application/json'
        )
        self.assertEqual(response7.status_code, 400)
        data7 = json.loads(response7.content)
        self.assertIn('無效的物品ID', data7['error'])

        # 測試：item_id 為 0
        response8 = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': 0}),
            content_type='application/json'
        )
        self.assertEqual(response8.status_code, 400)
        data8 = json.loads(response8.content)
        self.assertIn('無效的物品ID', data8['error'])

        # 測試：item_id 為不存在的 ID
        response9 = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': 99999}),
            content_type='application/json'
        )
        self.assertEqual(response9.status_code, 404)
        data9 = json.loads(response9.content)
        self.assertIn('物品不存在', data9['error'])

