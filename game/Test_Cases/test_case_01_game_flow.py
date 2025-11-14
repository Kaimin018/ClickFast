"""
遊戲流程測試用例
測試用例命名遵循 test_case_01_xxx 格式
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json
from game.models import (
    PlayerProfile, GameSession, ShopItem,
    PlayerPurchase, Achievement, PlayerAchievement
)


class GameFlowTestCase(TestCase):
    """遊戲流程測試類"""

    def setUp(self):
        """測試前準備"""
        self.client = Client()
        self.username = 'testuser'
        self.test_user = None

    def test_case_01_user_login_and_register(self):
        """測試用例 01: 用戶登錄和註冊"""
        # 測試新用戶註冊
        response = self.client.post(
            '/api/login/',
            data=json.dumps({'username': self.username}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['username'], self.username)
        self.assertIn('profile', data)
        self.assertEqual(data['profile']['coins'], 0)
        self.assertEqual(data['profile']['total_clicks'], 0)
        self.assertEqual(data['profile']['total_games_played'], 0)

        # 測試已存在用戶登錄
        response2 = self.client.post(
            '/api/login/',
            data=json.dumps({'username': self.username}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.content)
        self.assertTrue(data2['success'])

        # 測試空用戶名
        response3 = self.client.post(
            '/api/login/',
            data=json.dumps({'username': ''}),
            content_type='application/json'
        )
        self.assertEqual(response3.status_code, 400)

    def test_case_02_get_user_profile(self):
        """測試用例 02: 獲取用戶資料"""
        # 先登錄
        self.client.post(
            '/api/login/',
            data=json.dumps({'username': self.username}),
            content_type='application/json'
        )

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

    def test_case_03_submit_game_result(self):
        """測試用例 03: 提交遊戲結果"""
        # 先登錄
        self.client.post(
            '/api/login/',
            data=json.dumps({'username': self.username}),
            content_type='application/json'
        )

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

    def test_case_04_submit_game_with_extended_time(self):
        """測試用例 04: 提交延長時間的遊戲結果"""
        # 先登錄
        self.client.post(
            '/api/login/',
            data=json.dumps({'username': self.username}),
            content_type='application/json'
        )

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

    def test_case_05_get_shop_items(self):
        """測試用例 05: 獲取商店物品列表"""
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

    def test_case_06_purchase_shop_item(self):
        """測試用例 06: 購買商店物品"""
        # 創建商店物品
        shop_item = ShopItem.objects.create(
            name='時間延長',
            item_type='time_extension',
            description='延長遊戲時間',
            base_price=100,
            effect_value=5.0,
            max_level=10
        )

        # 先登錄
        self.client.post(
            '/api/login/',
            data=json.dumps({'username': self.username}),
            content_type='application/json'
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

    def test_case_07_get_achievements(self):
        """測試用例 07: 獲取成就列表"""
        # 創建測試成就
        achievement = Achievement.objects.create(
            name='首次點擊',
            description='完成第一次點擊',
            achievement_type='single_round',
            target_value=1,
            reward_coins=10,
            icon='🎯'
        )

        # 先登錄
        self.client.post(
            '/api/login/',
            data=json.dumps({'username': self.username}),
            content_type='application/json'
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

    def test_case_08_achievement_unlock(self):
        """測試用例 08: 成就解鎖"""
        # 創建測試成就
        achievement = Achievement.objects.create(
            name='點擊達人',
            description='單局點擊達到50次',
            achievement_type='single_round',
            target_value=50,
            reward_coins=100,
            icon='🏆'
        )

        # 先登錄
        self.client.post(
            '/api/login/',
            data=json.dumps({'username': self.username}),
            content_type='application/json'
        )

        # 提交達到成就目標的遊戲結果
        response = self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 50, 'game_duration': 10.0}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # 應該解鎖成就
        self.assertGreater(len(data['new_achievements']), 0)
        self.assertEqual(data['new_achievements'][0]['name'], achievement.name)

        # 驗證成就記錄
        player_achievement = PlayerAchievement.objects.filter(
            user__username=self.username,
            achievement=achievement
        ).first()
        self.assertIsNotNone(player_achievement)
        self.assertTrue(player_achievement.reward_claimed)

        # 驗證獎勵金幣已發放
        profile = PlayerProfile.objects.get(user__username=self.username)
        # 50次點擊 = 50金幣 + 成就獎勵100金幣 = 150金幣
        self.assertEqual(profile.coins, 150)

    def test_case_09_get_game_history(self):
        """測試用例 09: 獲取遊戲歷史記錄"""
        # 先登錄
        self.client.post(
            '/api/login/',
            data=json.dumps({'username': self.username}),
            content_type='application/json'
        )

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

    def test_case_10_complete_game_flow(self):
        """測試用例 10: 完整遊戲流程"""
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

    def test_case_11_update_best_clicks_record(self):
        """測試用例 11: 更新最佳點擊記錄"""
        # 先登錄
        self.client.post(
            '/api/login/',
            data=json.dumps({'username': self.username}),
            content_type='application/json'
        )

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

    def test_case_12_purchase_multiple_levels(self):
        """測試用例 12: 購買多個等級的物品"""
        # 創建商店物品
        shop_item = ShopItem.objects.create(
            name='自動點擊器',
            item_type='auto_clicker',
            description='自動點擊',
            base_price=100,
            effect_value=1.0,
            max_level=5
        )

        # 先登錄
        self.client.post(
            '/api/login/',
            data=json.dumps({'username': self.username}),
            content_type='application/json'
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

