"""
認證系統測試 - Session 管理
TC_AUTH_002: Session 持久性和登出功能測試
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
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

