"""
前端功能測試用例 - 桌面版和通用功能
測試用例命名遵循 test_case_03_xxx 格式
使用 Selenium 進行瀏覽器自動化測試
"""
from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from game.models import PlayerProfile, ShopItem


class FrontendFunctionalityTestCase(LiveServerTestCase):
    """前端功能測試類"""

    def setUp(self):
        """測試前準備"""
        # 設置 Chrome 選項（桌面版）
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 無頭模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')  # 桌面尺寸
        
        # 嘗試創建 WebDriver（使用 webdriver-manager 自動管理驅動）
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            # 如果 Chrome 不可用，跳過測試
            self.skipTest(f"Chrome WebDriver 不可用: {e}")
        
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        """測試後清理"""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def test_case_01_page_loads_successfully(self):
        """測試用例 01: 頁面成功載入"""
        self.driver.get(self.live_server_url)
        
        # 檢查頁面標題
        self.assertIn("ClickFast", self.driver.title)
        
        # 檢查主要元素是否存在
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertIsNotNone(body)

    def test_case_02_user_login_flow(self):
        """測試用例 02: 用戶登錄流程"""
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

    def test_case_03_game_start_and_click(self):
        """測試用例 03: 遊戲開始和點擊功能"""
        self.driver.get(self.live_server_url)
        
        # 登錄
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

    def test_case_04_timer_countdown(self):
        """測試用例 04: 計時器倒數功能"""
        self.driver.get(self.live_server_url)
        
        # 登錄
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
        
        # 開始遊戲
        start_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "startButton"))
        )
        start_button.click()
        
        # 獲取初始時間
        timer_display = self.driver.find_element(By.ID, "timerDisplay")
        initial_time = float(timer_display.text.replace(' 秒', ''))
        
        # 等待一小段時間
        time.sleep(1)
        
        # 檢查時間是否減少
        final_time = float(timer_display.text.replace(' 秒', ''))
        self.assertLess(final_time, initial_time)

    def test_case_05_shop_modal_open_close(self):
        """測試用例 05: 商店模態框打開和關閉"""
        self.driver.get(self.live_server_url)
        
        # 登錄
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
        
        # 打開商店
        shop_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '商店')]"))
        )
        shop_button.click()
        
        # 等待模態框出現
        shop_modal = self.wait.until(
            EC.presence_of_element_located((By.ID, "shopModal"))
        )
        self.assertTrue(shop_modal.is_displayed())
        
        # 關閉模態框
        close_button = shop_modal.find_element(By.CLASS_NAME, "close-btn")
        close_button.click()
        
        time.sleep(0.5)
        
        # 檢查模態框是否隱藏
        modal_classes = shop_modal.get_attribute("class")
        self.assertNotIn("active", modal_classes)

    def test_case_06_achievements_modal_open_close(self):
        """測試用例 06: 成就模態框打開和關閉"""
        self.driver.get(self.live_server_url)
        
        # 登錄
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
        
        # 打開成就
        achievement_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '成就')]"))
        )
        achievement_button.click()
        
        # 等待模態框出現
        achievement_modal = self.wait.until(
            EC.presence_of_element_located((By.ID, "achievementsModal"))
        )
        self.assertTrue(achievement_modal.is_displayed())
        
        # 關閉模態框
        close_button = achievement_modal.find_element(By.CLASS_NAME, "close-btn")
        close_button.click()
        
        time.sleep(0.5)
        
        # 檢查模態框是否隱藏
        modal_classes = achievement_modal.get_attribute("class")
        self.assertNotIn("active", modal_classes)

    def test_case_07_user_statistics_update(self):
        """測試用例 07: 用戶統計資訊更新"""
        self.driver.get(self.live_server_url)
        
        # 登錄
        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "usernameInput"))
        )
        username_input.send_keys("testuser")
        
        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '開始遊戲')]")
        login_button.click()
        
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

    def test_case_08_button_states(self):
        """測試用例 08: 按鈕狀態管理"""
        self.driver.get(self.live_server_url)
        
        # 登錄
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
        
        # 檢查主點擊按鈕初始狀態（應該被禁用）
        main_button = self.driver.find_element(By.ID, "mainClickButton")
        self.assertTrue(main_button.get_attribute("disabled") is not None)
        
        # 開始遊戲
        start_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "startButton"))
        )
        start_button.click()
        
        # 等待主按鈕啟用
        self.wait.until(
            lambda driver: driver.find_element(By.ID, "mainClickButton").get_attribute("disabled") is None
        )
        
        # 檢查主按鈕現在應該啟用
        main_button = self.driver.find_element(By.ID, "mainClickButton")
        self.assertIsNone(main_button.get_attribute("disabled"))

    def test_case_09_responsive_design_elements(self):
        """測試用例 09: 響應式設計元素"""
        self.driver.get(self.live_server_url)
        
        # 檢查容器是否存在
        container = self.driver.find_element(By.CLASS_NAME, "container")
        self.assertIsNotNone(container)
        
        # 檢查主要面板是否存在
        panels = self.driver.find_elements(By.CLASS_NAME, "panel")
        self.assertGreater(len(panels), 0)

    def test_case_10_css_classes_present(self):
        """測試用例 10: CSS 類別存在"""
        self.driver.get(self.live_server_url)
        
        # 登錄
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
        
        # 檢查關鍵 CSS 類別是否存在
        game_container = self.driver.find_element(By.CLASS_NAME, "game-container")
        self.assertIsNotNone(game_container)
        
        click_buttons_container = self.driver.find_element(By.ID, "clickButtonsContainer")
        self.assertIsNotNone(click_buttons_container)

