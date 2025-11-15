"""
UI系統測試 - 遊戲操作
TC_UI_005: 遊戲開始和點擊功能測試
"""
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


class GameOperationsTestCase(LiveServerTestCase):
    """遊戲操作測試類"""

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

    def test_game_start_and_click(self):
        """測試用例：遊戲開始和點擊功能"""
        # 開始遊戲
        start_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "startButton"))
        )
        start_button.click()
        
        # 等待點擊按鈕啟用
        main_button = self.wait.until(
            lambda driver: not driver.find_element(By.ID, "mainClickButton").get_attribute("disabled")
        )
        
        # 獲取初始點擊數
        clicks_display = self.driver.find_element(By.ID, "clicksDisplay")
        initial_text = clicks_display.text
        
        # 點擊按鈕
        main_button.click()
        time.sleep(0.2)
        
        # 檢查點擊數是否增加
        final_text = clicks_display.text
        self.assertNotEqual(initial_text, final_text)

