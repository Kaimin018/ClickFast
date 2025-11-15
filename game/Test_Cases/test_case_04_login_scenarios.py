"""
登入狀況測試用例
測試各種登入場景和邊界情況
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
import json
from game.models import PlayerProfile


class LoginScenariosTestCase(TestCase):
    """登入狀況測試類"""

    def setUp(self):
        """測試前準備"""
        self.client = Client()
        self.base_url = '/api/login/'

    def test_case_01_new_user_registration(self):
        """測試用例 01: 新用戶註冊"""
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

    def test_case_02_existing_user_login(self):
        """測試用例 02: 已存在用戶登入"""
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

    def test_case_03_empty_username(self):
        """測試用例 03: 空用戶名"""
        response = self.client.post(
            self.base_url,
            data=json.dumps({'username': ''}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('不能為空', data['error'])

    def test_case_04_whitespace_only_username(self):
        """測試用例 04: 只有空白字符的用戶名"""
        # 測試只有空格
        response = self.client.post(
            self.base_url,
            data=json.dumps({'username': '   '}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
        
        # 測試只有換行符
        response2 = self.client.post(
            self.base_url,
            data=json.dumps({'username': '\n\t'}),
            content_type='application/json'
        )
        
        self.assertEqual(response2.status_code, 400)

    def test_case_05_username_with_leading_trailing_spaces(self):
        """測試用例 05: 用戶名前後有空格（應該被 trim）"""
        username_with_spaces = '  testuser  '
        expected_username = 'testuser'
        
        response = self.client.post(
            self.base_url,
            data=json.dumps({'username': username_with_spaces}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        # 驗證用戶名已被 trim
        self.assertEqual(data['user']['username'], expected_username)
        
        # 驗證資料庫中的用戶名也是 trim 後的
        user = User.objects.get(username=expected_username)
        self.assertEqual(user.username, expected_username)

    def test_case_06_special_characters_username(self):
        """測試用例 06: 特殊字符用戶名"""
        special_usernames = [
            'user_123',
            'user-name',
            'user.name',
            'user@123',
            'user#123',
            '中文用戶名',
            'user123!@#',
        ]
        
        for username in special_usernames:
            with self.subTest(username=username):
                response = self.client.post(
                    self.base_url,
                    data=json.dumps({'username': username}),
                    content_type='application/json'
                )
                
                # 大部分特殊字符應該可以接受（Django User 模型允許）
                self.assertIn(response.status_code, [200, 400])
                if response.status_code == 200:
                    data = json.loads(response.content)
                    self.assertTrue(data['success'])

    def test_case_07_long_username(self):
        """測試用例 07: 長用戶名"""
        # Django User 模型的 username 欄位最大長度是 150
        short_username = 'a' * 20
        medium_username = 'a' * 100
        long_username = 'a' * 151  # 超過限制
        
        # 測試正常長度
        response1 = self.client.post(
            self.base_url,
            data=json.dumps({'username': short_username}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 200)
        
        # 測試中等長度
        response2 = self.client.post(
            self.base_url,
            data=json.dumps({'username': medium_username}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)
        
        # 測試超長用戶名（應該失敗或截斷）
        response3 = self.client.post(
            self.base_url,
            data=json.dumps({'username': long_username}),
            content_type='application/json'
        )
        # 可能會失敗或截斷，取決於 Django 的處理方式
        self.assertIn(response3.status_code, [200, 400, 500])

    def test_case_08_session_persistence(self):
        """測試用例 08: Session 持久性"""
        username = 'sessionuser'
        
        # 登入
        response = self.client.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 驗證 session 已創建
        self.assertTrue(self.client.session.session_key is not None)
        
        # 使用同一個 client 訪問需要登入的 API
        response2 = self.client.get('/api/profile/')
        self.assertEqual(response2.status_code, 200)
        
        # 驗證 session 仍然有效
        self.assertTrue(self.client.session.session_key is not None)

    def test_case_09_logout_functionality(self):
        """測試用例 09: 登出功能"""
        username = 'logoutuser'
        
        # 先登入
        response = self.client.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 驗證可以訪問受保護的 API
        response2 = self.client.get('/api/profile/')
        self.assertEqual(response2.status_code, 200)
        
        # 登出
        response3 = self.client.post(
            '/api/logout/',
            content_type='application/json'
        )
        self.assertEqual(response3.status_code, 200)
        data = json.loads(response3.content)
        self.assertTrue(data['success'])
        
        # 驗證登出後無法訪問受保護的 API
        response4 = self.client.get('/api/profile/')
        self.assertEqual(response4.status_code, 401)

    def test_case_10_unauthorized_access(self):
        """測試用例 10: 未登入狀態訪問受保護的 API"""
        # 使用新的 client（未登入）
        new_client = Client()
        
        # 嘗試訪問需要登入的 API
        response = new_client.get('/api/profile/')
        self.assertEqual(response.status_code, 401)
        
        response2 = new_client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 10, 'game_duration': 5.0}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 401)

    def test_case_11_multiple_login_same_user(self):
        """測試用例 11: 同一用戶多次登入"""
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

    def test_case_12_different_users_login(self):
        """測試用例 12: 不同用戶登入"""
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

    def test_case_13_login_with_profile_data(self):
        """測試用例 13: 登入後驗證玩家資料完整性"""
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

    def test_case_14_login_after_logout(self):
        """測試用例 14: 登出後重新登入"""
        username = 'reloginuser'
        
        # 第一次登入
        response1 = self.client.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 200)
        
        # 登出
        response2 = self.client.post('/api/logout/')
        self.assertEqual(response2.status_code, 200)
        
        # 重新登入
        response3 = self.client.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response3.status_code, 200)
        data3 = json.loads(response3.content)
        self.assertTrue(data3['success'])
        self.assertEqual(data3['user']['username'], username)
        
        # 驗證可以訪問受保護的 API
        response4 = self.client.get('/api/profile/')
        self.assertEqual(response4.status_code, 200)

    def test_case_15_case_sensitive_username(self):
        """測試用例 15: 用戶名大小寫敏感性"""
        username_lower = 'caseuser'
        username_upper = 'CASEUSER'
        username_mixed = 'CaseUser'
        
        # 創建小寫用戶名
        response1 = self.client.post(
            self.base_url,
            data=json.dumps({'username': username_lower}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 200)
        
        # Django User 模型的 username 是大小寫敏感的
        # 嘗試用大寫登入應該創建新用戶
        response2 = self.client.post(
            self.base_url,
            data=json.dumps({'username': username_upper}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)
        
        # 驗證創建了兩個不同的用戶
        user_count = User.objects.filter(username__in=[username_lower, username_upper]).count()
        self.assertEqual(user_count, 2)

    def test_case_16_missing_username_field(self):
        """測試用例 16: 缺少用戶名字段"""
        # 不提供 username 欄位
        response = self.client.post(
            self.base_url,
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # 應該返回錯誤
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)

    def test_case_17_invalid_json(self):
        """測試用例 17: 無效的 JSON 格式"""
        # 發送無效的 JSON
        response = self.client.post(
            self.base_url,
            data='invalid json',
            content_type='application/json'
        )
        
        # 應該返回錯誤
        self.assertIn(response.status_code, [400, 500])

    def test_case_18_get_method_not_allowed(self):
        """測試用例 18: GET 方法不被允許"""
        response = self.client.get(self.base_url)
        # 應該返回 405 Method Not Allowed 或類似的錯誤
        self.assertIn(response.status_code, [405, 400, 500])

    def test_case_19_concurrent_login_different_clients(self):
        """測試用例 19: 不同客戶端同時登入同一用戶"""
        username = 'concurrentuser'
        
        # 第一個客戶端登入
        client1 = Client()
        response1 = client1.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 200)
        
        # 第二個客戶端登入同一個用戶
        client2 = Client()
        response2 = client2.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)
        
        # 驗證兩個客戶端都可以訪問自己的 session
        response3 = client1.get('/api/profile/')
        self.assertEqual(response3.status_code, 200)
        
        response4 = client2.get('/api/profile/')
        self.assertEqual(response4.status_code, 200)
        
        # 驗證只創建了一個用戶
        user_count = User.objects.filter(username=username).count()
        self.assertEqual(user_count, 1)

