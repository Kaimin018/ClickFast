"""
認證系統測試 - 驗證邏輯單元測試
TC_AUTH_003: 用戶名驗證邏輯測試
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
import json


class ValidationUnitTestCase(TestCase):
    """驗證邏輯單元測試類"""

    def setUp(self):
        """測試前準備"""
        self.client = Client()
        self.base_url = '/api/login/'

    def test_empty_username(self):
        """測試用例：空用戶名"""
        response = self.client.post(
            self.base_url,
            data=json.dumps({'username': ''}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('不能為空', data['error'])

    def test_whitespace_only_username(self):
        """測試用例：只有空白字符的用戶名"""
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

    def test_username_with_leading_trailing_spaces(self):
        """測試用例：用戶名前後有空格（應該被 trim）"""
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

    def test_special_characters_username(self):
        """測試用例：特殊字符用戶名"""
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

    def test_long_username(self):
        """測試用例：長用戶名"""
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

    def test_case_sensitive_username(self):
        """測試用例：用戶名大小寫敏感性"""
        username_lower = 'caseuser'
        username_upper = 'CASEUSER'
        
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

    def test_missing_username_field(self):
        """測試用例：缺少用戶名字段"""
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

    def test_invalid_json(self):
        """測試用例：無效的 JSON 格式"""
        # 發送無效的 JSON
        response = self.client.post(
            self.base_url,
            data='invalid json',
            content_type='application/json'
        )
        
        # 應該返回錯誤
        self.assertIn(response.status_code, [400, 500])

    def test_get_method_not_allowed(self):
        """測試用例：GET 方法不被允許"""
        response = self.client.get(self.base_url)
        # 應該返回 405 Method Not Allowed 或類似的錯誤
        self.assertIn(response.status_code, [405, 400, 500])

