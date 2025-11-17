"""
前端響應式設計測試 - 手機版 Viewport
TC_RESP_001: 手機版 viewport 設置和響應式佈局測試
"""
from django.test import LiveServerTestCase
from game.Test_Cases.base_test_case import PostgreSQLLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


class MobileViewportTestCase(PostgreSQLLiveServerTestCase):
    """手機版 Viewport 測試類"""

    def setUp(self):
        """測試前準備"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1')
        chrome_options.add_argument('--window-size=375,667')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            self.skipTest(f"Chrome WebDriver 不可用: {e}")
        
        self.driver.set_window_size(375, 667)
        self.wait = WebDriverWait(self.driver, 10)
        self._disable_alerts()

    def _disable_alerts(self):
        """禁用 alert 彈窗"""
        try:
            self.driver.execute_script("""
                window.alert = function(msg) { console.log('Alert intercepted:', msg); };
                window.confirm = function(msg) { console.log('Confirm intercepted:', msg); return true; };
            """)
        except:
            pass
    
    def _handle_alert_if_present(self):
        """處理可能存在的 alert"""
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            self.driver.switch_to.default_content()
        except NoAlertPresentException:
            pass
        except Exception:
            pass

    def tearDown(self):
        """測試後清理"""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def test_mobile_viewport_settings(self):
        """測試用例：手機版 viewport 設置"""
        self.driver.get(self.live_server_url)
        
        # 檢查 viewport meta 標籤
        viewport_meta = self.driver.find_element(By.XPATH, "//meta[@name='viewport']")
        viewport_content = viewport_meta.get_attribute('content')
        
        # 驗證 viewport 設置包含防止縮放的選項
        self.assertIn('maximum-scale=1.0', viewport_content)
        self.assertIn('user-scalable=no', viewport_content)
        self.assertIn('width=device-width', viewport_content)

    def test_mobile_responsive_layout(self):
        """測試用例：手機版響應式佈局"""
        self.driver.get(self.live_server_url)
        
        # 等待頁面載入
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # 檢查容器寬度（應該適應手機螢幕）
        container = self.driver.find_element(By.CLASS_NAME, "container")
        container_width = container.size['width']
        
        # 在手機模式下，容器應該接近視窗寬度（考慮 padding）
        self.assertLessEqual(container_width, 500)  # 手機寬度應該小於等於 500px
        
        # 檢查 header 是否存在
        header = self.driver.find_element(By.CLASS_NAME, "header")
        self.assertIsNotNone(header)

    def test_mobile_login_interface(self):
        """測試用例：手機版登錄介面"""
        self.driver.get(self.live_server_url)
        
        # 等待登錄面板出現
        login_panel = self.wait.until(
            EC.presence_of_element_located((By.ID, "loginPanel"))
        )
        
        # 檢查登錄面板是否可見
        self.assertTrue(login_panel.is_displayed())
        
        # 檢查輸入框
        username_input = self.driver.find_element(By.ID, "usernameInput")
        self.assertTrue(username_input.is_displayed())
        
        # 檢查輸入框在手機上的寬度（應該接近全寬）
        input_width = username_input.size['width']
        self.assertGreater(input_width, 200)
        
        # 檢查登錄按鈕
        login_button = login_panel.find_element(By.XPATH, ".//button[contains(text(), '開始遊戲')]")
        self.assertTrue(login_button.is_displayed())

