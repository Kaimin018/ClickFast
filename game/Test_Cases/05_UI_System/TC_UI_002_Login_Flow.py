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


class LoginFlowTestCase(LiveServerTestCase):
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
        login_button.click()
        
        # 等待遊戲內容出現
        game_content = self.wait.until(
            EC.presence_of_element_located((By.ID, "gameContent"))
        )
        self.assertTrue(game_content.is_displayed())
        
        # 檢查登錄面板是否隱藏
        self.assertFalse(login_panel.is_displayed())

