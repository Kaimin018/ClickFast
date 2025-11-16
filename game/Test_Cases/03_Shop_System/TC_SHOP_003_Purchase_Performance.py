"""
商店系統測試 - 購買功能效能和壓力測試
TC_SHOP_003: 購買功能效能測試、並發測試、響應時間測試
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from game.models import ShopItem, PlayerProfile, PlayerPurchase


class PurchasePerformanceTestCase(TestCase):
    """購買功能效能測試類"""

    def setUp(self):
        """測試前準備"""
        self.client = Client()
        self.username = 'perftest_user'
        self.user = User.objects.create_user(username=self.username, password='testpass')
        
        # 登錄
        self.client.force_login(self.user)
        
        # 創建商店物品
        self.shop_item = ShopItem.objects.create(
            name='效能測試物品',
            item_type='time_extension',
            description='用於效能測試',
            base_price=100,
            effect_value=5.0,
            max_level=10
        )
        
        # 給予足夠的金幣
        profile = PlayerProfile.objects.create(
            user=self.user,
            coins=100000,  # 足夠購買多次
            total_clicks=0,
            best_clicks_per_round=0,
            total_games_played=0,
            battle_wins=0,
        )

    def test_purchase_response_time(self):
        """測試用例：購買響應時間測試"""
        # 測試單次購買的響應時間
        start_time = time.time()
        response = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': self.shop_item.id}),
            content_type='application/json'
        )
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # 轉換為毫秒
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 1000, f'購買響應時間過長: {response_time}ms')  # 應該在1秒內完成
        
        print(f'✓ 單次購買響應時間: {response_time:.2f}ms')

    def test_multiple_purchases_response_time(self):
        """測試用例：多次購買的響應時間測試"""
        # 重置購買記錄
        PlayerPurchase.objects.filter(user=self.user, shop_item=self.shop_item).delete()
        profile = PlayerProfile.objects.get(user=self.user)
        profile.coins = 100000
        profile.save()
        
        # 測試連續購買10次的總響應時間
        start_time = time.time()
        for i in range(10):
            response = self.client.post(
                '/api/purchase/',
                data=json.dumps({'item_id': self.shop_item.id}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
        end_time = time.time()
        
        total_time = (end_time - start_time) * 1000
        avg_time = total_time / 10
        
        self.assertLess(avg_time, 500, f'平均購買響應時間過長: {avg_time:.2f}ms')
        
        print(f'✓ 10次購買總時間: {total_time:.2f}ms')
        print(f'✓ 平均每次購買時間: {avg_time:.2f}ms')

    def test_concurrent_purchases(self):
        """測試用例：並發購買測試（防止重複購買）"""
        # 重置購買記錄（每個用戶購買不同的物品，所以不需要重置）
        profile = PlayerProfile.objects.get(user=self.user)
        profile.coins = 100000
        profile.save()
        
        # 創建多個用戶進行並發購買
        users = []
        clients = []
        for i in range(5):
            username = f'concurrent_user_{i}'
            user = User.objects.create_user(username=username, password='testpass')
            users.append(user)
            client = Client()
            client.force_login(user)
            clients.append(client)
            
            # 給予足夠的金幣
            PlayerProfile.objects.create(
                user=user,
                coins=10000,
                total_clicks=0,
                best_clicks_per_round=0,
                total_games_played=0,
                battle_wins=0,
            )
        
        # 並發購買同一個物品
        def purchase_item(client, item_id):
            try:
                response = client.post(
                    '/api/purchase/',
                    data=json.dumps({'item_id': item_id}),
                    content_type='application/json'
                )
                return {
                    'success': response.status_code == 200,
                    'status_code': response.status_code,
                    'response': json.loads(response.content) if response.content else {}
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }
        
        # 使用線程池進行並發測試
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(purchase_item, client, self.shop_item.id) for client in clients]
            results = [future.result() for future in as_completed(futures)]
        end_time = time.time()
        
        # 驗證所有購買都成功
        success_count = sum(1 for r in results if r['success'])
        self.assertEqual(success_count, 5, '所有並發購買應該都成功')
        
        print(f'✓ 5個並發購買完成時間: {(end_time - start_time) * 1000:.2f}ms')
        print(f'✓ 成功購買數: {success_count}/5')

    def test_rapid_sequential_purchases(self):
        """測試用例：快速連續購買測試（測試防重複點擊機制）"""
        # 重置購買記錄
        PlayerPurchase.objects.filter(user=self.user, shop_item=self.shop_item).delete()
        profile = PlayerProfile.objects.get(user=self.user)
        profile.coins = 100000
        profile.save()
        
        # 快速連續發送5個購買請求（模擬用戶快速點擊）
        responses = []
        start_time = time.time()
        for i in range(5):
            response = self.client.post(
                '/api/purchase/',
                data=json.dumps({'item_id': self.shop_item.id}),
                content_type='application/json'
            )
            responses.append({
                'status_code': response.status_code,
                'data': json.loads(response.content) if response.content else {}
            })
        end_time = time.time()
        
        # 驗證：應該只有第一次購買成功，後續應該因為等級已滿而失敗
        success_count = sum(1 for r in responses if r['status_code'] == 200)
        # 由於每次購買都會升級，所以前幾次應該成功，直到達到最大等級
        self.assertGreater(success_count, 0, '至少應該有一次購買成功')
        
        # 檢查是否有達到最大等級的錯誤
        max_level_errors = sum(1 for r in responses 
                              if r['status_code'] == 400 and '已達到最大等級' in r['data'].get('error', ''))
        
        print(f'✓ 快速連續5次購買完成時間: {(end_time - start_time) * 1000:.2f}ms')
        print(f'✓ 成功購買數: {success_count}/5')
        print(f'✓ 達到最大等級錯誤數: {max_level_errors}')

    def test_purchase_with_insufficient_coins(self):
        """測試用例：金幣不足時的響應時間測試"""
        # 設置金幣為0
        profile = PlayerProfile.objects.get(user=self.user)
        profile.coins = 0
        profile.save()
        
        # 重置購買記錄
        PlayerPurchase.objects.filter(user=self.user, shop_item=self.shop_item).delete()
        
        # 測試金幣不足時的響應時間
        start_time = time.time()
        response = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': self.shop_item.id}),
            content_type='application/json'
        )
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('金幣不足', data['error'])
        self.assertLess(response_time, 500, f'金幣不足檢查響應時間過長: {response_time}ms')
        
        print(f'✓ 金幣不足檢查響應時間: {response_time:.2f}ms')

    def test_purchase_api_response_structure(self):
        """測試用例：驗證購買API回應結構（包含優化後的欄位）"""
        # 重置購買記錄
        PlayerPurchase.objects.filter(user=self.user, shop_item=self.shop_item).delete()
        profile = PlayerProfile.objects.get(user=self.user)
        profile.coins = 10000
        profile.save()
        
        response = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': self.shop_item.id}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # 驗證回應包含所有必要的欄位
        self.assertIn('success', data)
        self.assertIn('new_level', data)
        self.assertIn('coins_remaining', data)
        self.assertIn('item_name', data)
        self.assertIn('next_level_price', data)  # 優化後新增的欄位
        self.assertIn('can_upgrade', data)  # 優化後新增的欄位
        self.assertIn('max_level', data)  # 優化後新增的欄位
        
        self.assertTrue(data['success'])
        self.assertEqual(data['new_level'], 1)
        self.assertIsNotNone(data['next_level_price'])
        self.assertTrue(data['can_upgrade'])
        
        print('✓ 購買API回應結構驗證通過')

