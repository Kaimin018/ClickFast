"""
商店系統測試 - 商店物品列表
TC_SHOP_001: 商店物品列表查詢測試
"""
from django.test import TestCase, Client
import json
from game.models import ShopItem


class ShopItemListTestCase(TestCase):
    """商店物品列表測試類"""

    def setUp(self):
        """測試前準備"""
        self.client = Client()
        self.username = 'testuser'

    def test_get_shop_items(self):
        """測試用例：獲取商店物品列表"""
        # 創建測試商店物品
        shop_item = ShopItem.objects.create(
            name='時間延長',
            item_type='time_extension',
            description='延長遊戲時間',
            base_price=100,
            effect_value=5.0,
            max_level=10
        )

        # 未登錄也可以查看商店
        response = self.client.get('/api/shop/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('items', data)
        self.assertGreater(len(data['items']), 0)
        item = data['items'][0]
        self.assertEqual(item['name'], shop_item.name)
        self.assertEqual(item['current_level'], 0)
        self.assertTrue(item['can_upgrade'])

        # 登錄後查看商店
        self.client.post(
            '/api/login/',
            data=json.dumps({'username': self.username}),
            content_type='application/json'
        )
        response2 = self.client.get('/api/shop/')
        self.assertEqual(response2.status_code, 200)

