"""
技術與非功能性測試 - 驗證和邊界情況
TC_TECH_002: 參數驗證和邊界情況測試（包含前端單元測試）
"""
from django.test import TestCase, Client, LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import time


class ValidationEdgeCasesTestCase(TestCase):
    """驗證和邊界情況測試類（後端）"""

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

    def test_submit_game_invalid_clicks(self):
        """測試用例：提交遊戲結果 - 無效的點擊數"""
        # 測試負數點擊數
        response = self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': -10, 'game_duration': 10.0}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # 測試非數字點擊數
        response2 = self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 'invalid', 'game_duration': 10.0}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 400)

    def test_submit_game_invalid_duration(self):
        """測試用例：提交遊戲結果 - 無效的遊戲時長"""
        # 測試負數時長
        response = self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 50, 'game_duration': -10.0}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # 測試零時長
        response2 = self.client.post(
            '/api/submit-game/',
            data=json.dumps({'clicks': 50, 'game_duration': 0.0}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 400)

    def test_purchase_invalid_item_id(self):
        """測試用例：購買物品 - 無效的物品 ID"""
        # 測試不存在的物品 ID（應該返回 404，因為資源不存在）
        response = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': 99999}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        
        # 測試非數字物品 ID（應該返回 400，因為格式無效）
        response2 = self.client.post(
            '/api/purchase/',
            data=json.dumps({'item_id': 'invalid'}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 400)

    def test_history_invalid_limit(self):
        """測試用例：獲取歷史記錄 - 無效的 limit 參數"""
        # 測試負數 limit
        response = self.client.get('/api/history/?limit=-1')
        self.assertEqual(response.status_code, 400)
        
        # 測試超過最大值的 limit
        response2 = self.client.get('/api/history/?limit=1000')
        self.assertEqual(response2.status_code, 400)
        
        # 測試非數字 limit
        response3 = self.client.get('/api/history/?limit=invalid')
        self.assertEqual(response3.status_code, 400)


class FrontendUnitTestCase(LiveServerTestCase):
    """前端單元測試類"""

    def setUp(self):
        """測試前準備"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            self.skipTest(f"Chrome WebDriver 不可用: {e}")
        
        self.wait = WebDriverWait(self.driver, 10)
        
        # 登錄
        self.driver.get(self.live_server_url)
        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "usernameInput"))
        )
        username_input.send_keys("testuser")
        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '開始遊戲')]")
        login_button.click()
        self.wait.until(
            EC.presence_of_element_located((By.ID, "gameContent"))
        )

    def tearDown(self):
        """測試後清理"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def _fixture_teardown(self):
        """自定義 tearDown，避免 PostgreSQL 外鍵約束問題"""
        # 跳過 flush，因為 PostgreSQL 不支持在有外鍵約束時 truncate
        # 使用 --keepdb 選項運行測試可以避免這個問題
        pass

    def _close_all_modals(self):
        """關閉所有可能打開的 modal"""
        modal_ids = ['shopModal', 'achievementsModal', 'accountModal', 
                     'historyModal', 'achievementNotification', 'badgeSelectModal']
        for modal_id in modal_ids:
            try:
                modal = self.driver.find_element(By.ID, modal_id)
                # 檢查 modal 是否可見
                if modal.is_displayed() and 'active' in modal.get_attribute('class'):
                    # 嘗試點擊關閉按鈕
                    try:
                        close_btn = modal.find_element(By.CLASS_NAME, "close-btn")
                        if close_btn.is_displayed():
                            close_btn.click()
                            time.sleep(0.2)
                    except:
                        # 如果找不到關閉按鈕，嘗試點擊 modal 外部區域
                        try:
                            self.driver.execute_script(
                                f"document.getElementById('{modal_id}').classList.remove('active');"
                            )
                            time.sleep(0.2)
                        except:
                            pass
            except:
                pass
        # 額外等待確保 modal 完全關閉
        time.sleep(0.3)

    def test_timer_countdown(self):
        """測試用例：計時器倒數功能（單元測試）"""
        # 確保所有 modal 都已關閉
        self._close_all_modals()
        
        # 開始遊戲
        start_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "startButton"))
        )
        # 使用 JavaScript 點擊，避免被其他元素遮擋
        self.driver.execute_script("arguments[0].click();", start_button)
        
        # 獲取初始時間
        timer_display = self.driver.find_element(By.ID, "timerDisplay")
        initial_time = float(timer_display.text.replace(' 秒', ''))
        
        # 等待一小段時間
        time.sleep(1)
        
        # 檢查時間是否減少
        final_time = float(timer_display.text.replace(' 秒', ''))
        self.assertLess(final_time, initial_time)

    def test_button_states(self):
        """測試用例：按鈕狀態管理（單元測試）"""
        # 確保所有 modal 都已關閉
        self._close_all_modals()
        
        # 檢查主點擊按鈕初始狀態（應該被禁用）
        main_button = self.driver.find_element(By.ID, "mainClickButton")
        self.assertTrue(main_button.get_attribute("disabled") is not None)
        
        # 開始遊戲
        start_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "startButton"))
        )
        # 使用 JavaScript 點擊，避免被其他元素遮擋
        self.driver.execute_script("arguments[0].click();", start_button)
        
        # 等待主按鈕啟用
        self.wait.until(
            lambda driver: driver.find_element(By.ID, "mainClickButton").get_attribute("disabled") is None
        )
        
        # 檢查主按鈕現在應該啟用
        main_button = self.driver.find_element(By.ID, "mainClickButton")
        self.assertIsNone(main_button.get_attribute("disabled"))

