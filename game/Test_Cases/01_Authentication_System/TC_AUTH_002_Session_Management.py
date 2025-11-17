"""
認證系統測試 - Session 管理
TC_AUTH_002: Session 持久性和登出功能測試
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
import json
from game.models import PlayerProfile


class SessionManagementTestCase(TestCase):
    """Session 管理測試類"""

    def setUp(self):
        """測試前準備"""
        self.client = Client()
        self.base_url = '/api/login/'

    def test_session_persistence(self):
        """測試用例：Session 持久性"""
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

    def test_logout_functionality(self):
        """測試用例：登出功能"""
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

    def test_login_after_logout(self):
        """測試用例：登出後重新登入"""
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

    def test_unauthorized_access(self):
        """測試用例：未登入狀態訪問受保護的 API"""
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

    def test_single_session_strategy_new_user(self):
        """測試用例：新用戶登入不會清除任何 session（因為沒有舊的）"""
        username = 'newuser_single_session'
        
        # 新用戶登入
        response = self.client.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # 驗證用戶已創建
        user = User.objects.get(username=username)
        self.assertIsNotNone(user)
        
        # 驗證只有一個 session（新用戶的 session）
        user_sessions = self._get_user_sessions(user.id)
        self.assertEqual(len(user_sessions), 1)
        
        # 驗證可以訪問受保護的 API
        response2 = self.client.get('/api/profile/')
        self.assertEqual(response2.status_code, 200)

    def test_single_session_strategy_existing_user(self):
        """測試用例：已存在用戶在新裝置登入時，舊 session 會被清除"""
        username = 'existinguser_single_session'
        
        # 創建用戶（模擬已存在的用戶）
        user = User.objects.create_user(username=username)
        user.set_unusable_password()
        user.save()
        
        # 裝置 1 登入
        client1 = Client()
        response1 = client1.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 200)
        
        # 驗證裝置 1 的 session 已創建
        session_key_1 = client1.session.session_key
        self.assertIsNotNone(session_key_1)
        
        # 驗證裝置 1 可以訪問受保護的 API
        response1_profile = client1.get('/api/profile/')
        self.assertEqual(response1_profile.status_code, 200)
        
        # 驗證只有一個 session（裝置 1 的）
        user_sessions_before = self._get_user_sessions(user.id)
        self.assertEqual(len(user_sessions_before), 1)
        self.assertIn(session_key_1, [s.session_key for s in user_sessions_before])
        
        # 裝置 2 登入（應該清除裝置 1 的 session）
        client2 = Client()
        response2 = client2.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)
        
        # 驗證裝置 2 的 session 已創建
        session_key_2 = client2.session.session_key
        self.assertIsNotNone(session_key_2)
        self.assertNotEqual(session_key_1, session_key_2)
        
        # 驗證裝置 1 的 session 已被清除
        user_sessions_after = self._get_user_sessions(user.id)
        self.assertEqual(len(user_sessions_after), 1)
        self.assertIn(session_key_2, [s.session_key for s in user_sessions_after])
        self.assertNotIn(session_key_1, [s.session_key for s in user_sessions_after])
        
        # 驗證裝置 1 無法再訪問受保護的 API（session 已失效）
        response1_profile_after = client1.get('/api/profile/')
        self.assertEqual(response1_profile_after.status_code, 401)
        
        # 驗證裝置 2 可以訪問受保護的 API
        response2_profile = client2.get('/api/profile/')
        self.assertEqual(response2_profile.status_code, 200)

    def test_single_session_strategy_multiple_sessions(self):
        """測試用例：清除多個舊 session"""
        username = 'multisession_user'
        
        # 創建用戶
        user = User.objects.create_user(username=username)
        user.set_unusable_password()
        user.save()
        
        # 創建多個 session（模擬多個裝置登入）
        clients = []
        session_keys = []
        
        for i in range(3):
            client = Client()
            response = client.post(
                self.base_url,
                data=json.dumps({'username': username}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            clients.append(client)
            session_keys.append(client.session.session_key)
        
        # 驗證最後只有一個 session（最後一個登入的）
        user_sessions = self._get_user_sessions(user.id)
        self.assertEqual(len(user_sessions), 1)
        self.assertIn(session_keys[-1], [s.session_key for s in user_sessions])
        
        # 驗證前兩個 session 已被清除
        self.assertNotIn(session_keys[0], [s.session_key for s in user_sessions])
        self.assertNotIn(session_keys[1], [s.session_key for s in user_sessions])
        
        # 驗證只有最後一個 client 可以訪問受保護的 API
        for i, client in enumerate(clients):
            response = client.get('/api/profile/')
            if i == len(clients) - 1:
                # 最後一個應該可以訪問
                self.assertEqual(response.status_code, 200)
            else:
                # 其他的應該無法訪問
                self.assertEqual(response.status_code, 401)

    def test_single_session_strategy_same_device_relogin(self):
        """測試用例：同一裝置重新登入不會清除自己的 session"""
        username = 'relogin_same_device'
        
        # 第一次登入
        response1 = self.client.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 200)
        
        session_key_1 = self.client.session.session_key
        self.assertIsNotNone(session_key_1)
        
        # 驗證可以訪問受保護的 API
        response1_profile = self.client.get('/api/profile/')
        self.assertEqual(response1_profile.status_code, 200)
        
        # 同一裝置重新登入
        response2 = self.client.post(
            self.base_url,
            data=json.dumps({'username': username}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)
        
        # 驗證 session key 可能改變（因為重新登入），但應該仍然有效
        # 注意：Django 可能會重用同一個 session 或創建新的
        session_key_2 = self.client.session.session_key
        self.assertIsNotNone(session_key_2)
        
        # 驗證仍然可以訪問受保護的 API
        response2_profile = self.client.get('/api/profile/')
        self.assertEqual(response2_profile.status_code, 200)

    def _get_user_sessions(self, user_id):
        """輔助方法：獲取指定用戶的所有活躍 session"""
        active_sessions = Session.objects.filter(
            expire_date__gte=timezone.now()
        )
        user_sessions = []
        for session in active_sessions:
            try:
                session_data = session.get_decoded()
                if session_data.get('_auth_user_id') == str(user_id):
                    user_sessions.append(session)
            except Exception:
                # 如果 session 資料解碼失敗，跳過
                continue
        return user_sessions

