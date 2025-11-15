"""
UI系統測試 - 模態框操作
TC_UI_003: 商店和成就模態框打開和關閉測試
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


class ModalOperationsTestCase(LiveServerTestCase):
    """模態框操作測試類"""

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

    def test_shop_modal_open_close(self):
        """測試用例：商店模態框打開和關閉"""
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

    def test_achievements_modal_open_close(self):
        """測試用例：成就模態框打開和關閉"""
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

