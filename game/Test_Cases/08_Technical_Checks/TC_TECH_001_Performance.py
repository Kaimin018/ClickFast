"""
技術與非功能性測試 - 性能測試
TC_TECH_001: API 響應時間和資料庫查詢效能測試
"""
from django.test import TestCase, Client
from django.conf import settings
import json
import time
import os


class PerformanceTestCase(TestCase):
    """性能測試類"""

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
        
        # 根據環境決定性能閾值
        # 本地環境（localhost/127.0.0.1）使用較寬鬆的閾值
        # 雲端環境（CI/CD、Vercel、Render 等）使用嚴格的閾值
        self._determine_performance_threshold()
    
    def _determine_performance_threshold(self):
        """根據環境決定性能測試閾值"""
        # 檢查是否為 CI 環境
        is_ci = os.getenv('GITHUB_ACTIONS') or os.getenv('CI')
        
        # 檢查是否為雲端部署環境
        is_cloud = os.getenv('VERCEL') or os.getenv('RENDER') or os.getenv('HEROKU')
        
        # 檢查資料庫主機是否為本地
        # 在測試環境中，Django 會創建測試資料庫，但主機配置仍然反映實際環境
        db_host = None
        db_engine = None
        if hasattr(settings, 'DATABASES') and 'default' in settings.DATABASES:
            db_config = settings.DATABASES['default']
            db_host = db_config.get('HOST', '')
            db_engine = db_config.get('ENGINE', '')
        
        # 判斷是否為本地環境：
        # 1. 使用 SQLite（本地開發常用）
        # 2. PostgreSQL 主機為 localhost/127.0.0.1
        # 3. 沒有設置主機（SQLite 或本地 PostgreSQL）
        is_sqlite = 'sqlite' in db_engine.lower() if db_engine else False
        is_local_db = (
            is_sqlite or 
            db_host in ('localhost', '127.0.0.1', '::1', '') or 
            not db_host
        )
        
        # 如果是 CI 或雲端環境，使用嚴格閾值（1 秒）
        # 如果是本地環境，使用寬鬆閾值（3 秒）
        if is_ci or is_cloud or not is_local_db:
            self.performance_threshold = 1.0  # 雲端環境：1 秒
            self.environment = "雲端/CI"
        else:
            self.performance_threshold = 3.0  # 本地環境：3 秒
            self.environment = "本地"

    def test_api_response_time(self):
        """測試用例：API 響應時間"""
        # 測試登錄 API 響應時間
        start_time = time.time()
        response = self.client.post(
            '/api/login/',
            data=json.dumps({'username': 'perftest'}),
            content_type='application/json'
        )
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        # 根據環境使用不同的性能閾值
        self.assertLess(
            elapsed_time, 
            self.performance_threshold, 
            f"[{self.environment}環境] API 響應時間過長: {elapsed_time:.3f}秒 (閾值: {self.performance_threshold}秒)"
        )

    def test_submit_game_response_time(self):
        """測試用例：提交遊戲結果 API 響應時間"""
        start_time = time.time()
        response = self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 100, 'game_duration': 10.0}),
            content_type='application/json'
        )
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        # 根據環境使用不同的性能閾值
        self.assertLess(
            elapsed_time, 
            self.performance_threshold, 
            f"[{self.environment}環境] API 響應時間過長: {elapsed_time:.3f}秒 (閾值: {self.performance_threshold}秒)"
        )

    def test_profile_api_response_time(self):
        """測試用例：獲取資料 API 響應時間"""
        start_time = time.time()
        response = self.client.get('/api/profile/')
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        # 根據環境使用不同的性能閾值
        self.assertLess(
            elapsed_time, 
            self.performance_threshold, 
            f"[{self.environment}環境] API 響應時間過長: {elapsed_time:.3f}秒 (閾值: {self.performance_threshold}秒)"
        )

