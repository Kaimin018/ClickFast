"""
UI系統測試 - 登錄流程
TC_UI_002: 用戶登錄流程測試
"""
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from game.Test_Cases.base_test_case import PostgreSQLLiveServerTestCase
import time


class LoginFlowTestCase(PostgreSQLLiveServerTestCase):
    """登錄流程測試類"""

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

    def tearDown(self):
        """測試後清理"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def _wait_for_loading_to_disappear(self, timeout=10):
        """等待 loading modal 或 spinner 消失"""
        try:
            # 等待 loading modal 消失
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
        
        # 額外等待一小段時間確保動畫完成
        time.sleep(0.3)

    def test_user_login_flow(self):
        """測試用例：用戶登錄流程"""
        self.driver.get(self.live_server_url)
        
        # 等待登錄面板出現
        login_panel = self.wait.until(
            EC.presence_of_element_located((By.ID, "loginPanel"))
        )
        self.assertTrue(login_panel.is_displayed())
        
        # 輸入用戶名
        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "usernameInput"))
        )
        username_input.send_keys("testuser")
        
        # 點擊登錄按鈕
        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '開始遊戲')]")
        # 使用 JavaScript 點擊，避免被其他元素遮擋
        self.driver.execute_script("arguments[0].click();", login_button)
        
        # 等待 loading 消失
        self._wait_for_loading_to_disappear()
        
        # 等待遊戲內容出現
        game_content = self.wait.until(
            EC.presence_of_element_located((By.ID, "gameContent"))
        )
        self.assertTrue(game_content.is_displayed())
        
        # 檢查登錄面板是否隱藏
        self.assertFalse(login_panel.is_displayed())

