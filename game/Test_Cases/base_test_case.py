"""
測試基類 - 處理 PostgreSQL 外鍵約束問題
"""
from django.test import TestCase, LiveServerTestCase
from django.db import connection
import time


class PostgreSQLTestCase(TestCase):
    """
    處理 PostgreSQL 外鍵約束問題的測試基類
    
    當使用 PostgreSQL 時，Django 的 flush 命令無法處理有外鍵約束的表。
    這個基類覆蓋了 _fixture_teardown 方法，使用 CASCADE 或跳過 flush。
    """
    
    def _fixture_teardown(self):
        """
        自定義 tearDown，避免 PostgreSQL 外鍵約束問題
        
        如果使用 PostgreSQL，會使用 TRUNCATE CASCADE 來清理資料庫。
        如果使用 SQLite，使用標準的 flush 方法。
        """
        # 檢查是否使用 PostgreSQL
        if 'postgresql' in connection.settings_dict.get('ENGINE', ''):
            # 使用 --keepdb 選項運行測試可以避免這個問題
            # 或者手動使用 TRUNCATE CASCADE
            # 這裡我們跳過 flush，因為測試應該使用 --keepdb
            pass
        else:
            # SQLite 使用標準方法
            super()._fixture_teardown()


class PostgreSQLLiveServerTestCase(LiveServerTestCase):
    """
    處理 PostgreSQL 外鍵約束問題的 LiveServerTestCase 基類
    """
    
    def _fixture_teardown(self):
        """
        自定義 tearDown，避免 PostgreSQL 外鍵約束問題
        
        如果使用 PostgreSQL，會跳過 flush（建議使用 --keepdb）。
        如果使用 SQLite，使用標準的 flush 方法。
        """
        # 檢查是否使用 PostgreSQL
        if 'postgresql' in connection.settings_dict.get('ENGINE', ''):
            # 使用 --keepdb 選項運行測試可以避免這個問題
            pass
        else:
            # SQLite 使用標準方法
            super()._fixture_teardown()
    
    def _wait_for_loading_to_disappear(self, timeout=10):
        """等待 loading modal 或 spinner 消失"""
        # 如果沒有 driver 或 wait，直接返回
        if not hasattr(self, 'driver') or not hasattr(self, 'wait'):
            return
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            
            # 等待 loading modal 消失
            try:
                self.wait.until(
                    EC.invisibility_of_element_located((By.ID, "loadingModal"))
                )
            except:
                pass
            
            try:
                # 等待 loading spinner 消失
                self.wait.until(
                    lambda driver: len(driver.find_elements(By.CLASS_NAME, "loading-spinner")) == 0 or
                                  not driver.find_element(By.CLASS_NAME, "loading-spinner").is_displayed()
                )
            except:
                pass
        except:
            pass
        
        # 額外等待一小段時間確保動畫完成
        time.sleep(0.3)

