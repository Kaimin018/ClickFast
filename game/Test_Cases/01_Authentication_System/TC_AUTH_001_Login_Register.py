"""
認證系統測試 - 登錄與註冊功能
TC_AUTH_001: 用戶登錄和註冊功能測試
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
import json
from game.models import PlayerProfile


class LoginRegisterTestCase(TestCase):
    """登錄與註冊功能測試類"""

    def setUp(self):
        """測試前準備"""
        self.client = Client()
        self.base_url = '/api/login/'

    def test_new_user_registration(self):
        """測試用例：新用戶註冊"""
        username = 'newuser123'
        response = self.client.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['username'], username)
        self.assertIn('profile', data)
        
        # 驗證用戶已創建
        user = User.objects.get(username=username)
        self.assertIsNotNone(user)
        
        # 驗證玩家資料已創建
        profile = PlayerProfile.objects.get(user=user)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.coins, 0)
        self.assertEqual(profile.total_clicks, 0)
        self.assertEqual(profile.total_games_played, 0)

    def test_existing_user_login(self):
        """測試用例：已存在用戶登入"""
        username = 'existinguser'
        
        # 先創建用戶
        user = User.objects.create_user(username=username)
        PlayerProfile.objects.create(user=user)
        
        # 測試登入
        response = self.client.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['username'], username)
        
        # 驗證用戶資料沒有重複創建
        user_count = User.objects.filter(username=username).count()
        self.assertEqual(user_count, 1)

    def test_login_with_profile_data(self):
        """測試用例：登入後驗證玩家資料完整性"""
        username = 'profileuser'
        
        # 登入
        response = self.client.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # 驗證返回的資料結構
        self.assertIn('profile', data)
        profile = data['profile']
        
        # 驗證所有必要的欄位都存在
        required_fields = [
            'username', 'created_at', 'battle_wins', 'coins',
            'total_clicks', 'best_clicks_per_round', 'total_games_played'
        ]
        for field in required_fields:
            self.assertIn(field, profile)
        
        # 驗證初始值
        self.assertEqual(profile['coins'], 0)
        self.assertEqual(profile['total_clicks'], 0)
        self.assertEqual(profile['best_clicks_per_round'], 0)
        self.assertEqual(profile['total_games_played'], 0)
        self.assertEqual(profile['battle_wins'], 0)

    def test_multiple_login_same_user(self):
        """測試用例：同一用戶多次登入"""
        username = 'multiloginuser'
        
        # 第一次登入
        response1 = self.client.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 200)
        data1 = json.loads(response1.content)
        user_id_1 = data1['user']['id']
        
        # 第二次登入（使用同一個 client）
        response2 = self.client.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.content)
        user_id_2 = data2['user']['id']
        
        # 驗證是同一個用戶
        self.assertEqual(user_id_1, user_id_2)
        
        # 驗證用戶資料沒有重複
        user_count = User.objects.filter(username=username).count()
        self.assertEqual(user_count, 1)
        profile_count = PlayerProfile.objects.filter(user__username=username).count()
        self.assertEqual(profile_count, 1)

    def test_different_users_login(self):
        """測試用例：不同用戶登入"""
        username1 = 'user1'
        username2 = 'user2'
        
        # 登入第一個用戶
        response1 = self.client.post(
            self.base_url,
            data=json.dumps({'username': username1}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 200)
        data1 = json.loads(response1.content)
        user_id_1 = data1['user']['id']
        
        # 登入第二個用戶（使用同一個 client，會替換 session）
        response2 = self.client.post(
            self.base_url,
            data=json.dumps({'username': username2}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.content)
        user_id_2 = data2['user']['id']
        
        # 驗證是不同用戶
        self.assertNotEqual(user_id_1, user_id_2)
        
        # 驗證當前 session 屬於第二個用戶
        response3 = self.client.get('/api/profile/')
        self.assertEqual(response3.status_code, 200)
        data3 = json.loads(response3.content)
        self.assertEqual(data3['profile']['username'], username2)

    def test_concurrent_login_different_clients(self):
        """測試用例：不同客戶端登入同一用戶（單一會話策略）"""
        username = 'concurrentuser'
        
        # 第一個客戶端登入
        client1 = Client()
        response1 = client1.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 200)
        
        # 驗證第一個客戶端可以訪問 API
        response1_profile = client1.get('/api/profile/')
        self.assertEqual(response1_profile.status_code, 200)
        
        # 第二個客戶端登入同一個用戶（應該清除第一個客戶端的 session）
        client2 = Client()
        response2 = client2.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)
        
        # 驗證第一個客戶端的 session 已被清除，無法再訪問 API（單一會話策略）
        response3 = client1.get('/api/profile/')
        self.assertEqual(response3.status_code, 401, 
                        '第一個客戶端的 session 應該已被清除，無法訪問 API')
        
        # 驗證第二個客戶端可以訪問 API
        response4 = client2.get('/api/profile/')
        self.assertEqual(response4.status_code, 200)
        data4 = json.loads(response4.content)
        self.assertEqual(data4['profile']['username'], username)
        
        # 驗證只創建了一個用戶
        user_count = User.objects.filter(username=username).count()
        self.assertEqual(user_count, 1)

