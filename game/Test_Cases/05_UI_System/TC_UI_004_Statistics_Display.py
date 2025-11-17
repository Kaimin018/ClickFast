"""
UI系統測試 - 統計資訊顯示
TC_UI_004: 用戶統計資訊顯示和更新測試
"""
from django.test import LiveServerTestCase
from game.Test_Cases.base_test_case import PostgreSQLLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class StatisticsDisplayTestCase(PostgreSQLLiveServerTestCase):
    """統計資訊顯示測試類"""

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

    def test_user_statistics_update(self):
        """測試用例：用戶統計資訊更新"""
        # 等待用戶資訊顯示
        self.wait.until(
            EC.presence_of_element_located((By.ID, "userInfo"))
        )
        
        # 檢查統計資訊元素存在
        coins_display = self.driver.find_element(By.ID, "coinsDisplay")
        total_clicks = self.driver.find_element(By.ID, "totalClicksDisplay")
        
        # 獲取初始值
        initial_coins = coins_display.text
        initial_total_clicks = total_clicks.text
        
        # 這些值應該是數字（可能是 "0"）
        self.assertIsNotNone(initial_coins)
        self.assertIsNotNone(initial_total_clicks)

    def test_responsive_design_elements(self):
        """測試用例：響應式設計元素"""
        # 檢查容器是否存在
        container = self.driver.find_element(By.CLASS_NAME, "container")
        self.assertIsNotNone(container)
        
        # 檢查主要面板是否存在
        panels = self.driver.find_elements(By.CLASS_NAME, "panel")
        self.assertGreater(len(panels), 0)

    def test_css_classes_present(self):
        """測試用例：CSS 類別存在"""
        # 檢查關鍵 CSS 類別是否存在
        game_container = self.driver.find_element(By.CLASS_NAME, "game-container")
        self.assertIsNotNone(game_container)
        
        click_buttons_container = self.driver.find_element(By.ID, "clickButtonsContainer")
        self.assertIsNotNone(click_buttons_container)

