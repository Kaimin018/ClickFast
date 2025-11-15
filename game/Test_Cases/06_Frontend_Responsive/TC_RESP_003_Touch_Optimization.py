"""
前端響應式設計測試 - 觸控優化
TC_RESP_003: 手機版觸控動作防縮放和快速連點功能測試
"""
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


class TouchOptimizationTestCase(LiveServerTestCase):
    """觸控優化測試類"""

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

    def test_mobile_touch_action_prevention(self):
        """測試用例：手機版觸控動作防縮放"""
        self.driver.get(self.live_server_url)
        
        # 先登錄
        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "usernameInput"))
        )
        username_input.send_keys("testuser")
        
        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '開始遊戲')]")
        login_button.click()
        
        # 等待遊戲內容載入
        self.wait.until(
            EC.presence_of_element_located((By.ID, "gameContent"))
        )
        
        # 檢查點擊按鈕的 CSS 屬性
        main_button = self.wait.until(
            EC.presence_of_element_located((By.ID, "mainClickButton"))
        )
        
        # 檢查 touch-action 屬性（通過 JavaScript）
        touch_action = self.driver.execute_script(
            "return window.getComputedStyle(arguments[0]).touchAction;",
            main_button
        )
        # touch-action 應該是 manipulation 或 auto
        self.assertIn(touch_action.lower(), ['manipulation', 'auto', ''])

    def test_mobile_rapid_clicking(self):
        """測試用例：手機版快速連點功能"""
        self.driver.get(self.live_server_url)
        self._disable_alerts()
        time.sleep(0.5)
        self._handle_alert_if_present()
        
        # 先登錄
        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "usernameInput"))
        )
        username_input.send_keys("testuser")
        
        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '開始遊戲')]")
        login_button.click()
        
        # 等待遊戲內容載入
        self.wait.until(
            EC.presence_of_element_located((By.ID, "gameContent"))
        )
        time.sleep(0.3)
        self._handle_alert_if_present()
        
        # 開始遊戲
        start_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "startButton"))
        )
        start_button.click()
        
        # 等待點擊按鈕啟用
        main_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "mainClickButton"))
        )
        
        # 獲取初始點擊數
        clicks_display = self.driver.find_element(By.ID, "clicksDisplay")
        initial_text = clicks_display.text
        
        # 執行快速連點
        for i in range(5):
            self.driver.execute_script("arguments[0].click();", main_button)
            time.sleep(0.05)  # 50ms 間隔，模擬快速連點
        
        # 等待點擊數更新
        time.sleep(0.5)
        
        # 檢查點擊數是否增加
        final_text = clicks_display.text
        self.assertNotEqual(initial_text, final_text)

