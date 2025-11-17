"""
前端響應式設計測試 - 手機版佈局
TC_RESP_002: 手機版按鈕大小、控制佈局、統計資訊顯示測試
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


class MobileLayoutTestCase(PostgreSQLLiveServerTestCase):
    """手機版佈局測試類"""

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

    def _login(self):
        """登錄輔助方法"""
        self.driver.get(self.live_server_url)
        self._disable_alerts()
        time.sleep(0.5)
        self._handle_alert_if_present()
        
        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "usernameInput"))
        )
        username_input.send_keys("testuser")
        
        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '開始遊戲')]")
        login_button.click()
        
        self.wait.until(
            EC.presence_of_element_located((By.ID, "gameContent"))
        )
        time.sleep(0.3)
        self._handle_alert_if_present()

    def test_mobile_click_button_size(self):
        """測試用例：手機版點擊按鈕大小"""
        self._login()
        
        # 確保沒有 loading
        self._wait_for_loading_to_disappear()
        # 開始遊戲以啟用按鈕
        start_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "startButton"))
        )
        # 使用 JavaScript 點擊，避免被其他元素遮擋
        self.driver.execute_script("arguments[0].click();", start_button)
        # 等待 loading 消失
        self._wait_for_loading_to_disappear()
        time.sleep(0.5)
        self._handle_alert_if_present()
        
        # 等待點擊按鈕啟用並可見
        main_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "mainClickButton"))
        )
        
        time.sleep(0.5)
        main_button = self.driver.find_element(By.ID, "mainClickButton")
        
        # 檢查按鈕大小（手機上應該更大）
        button_height = main_button.size['height']
        button_width = main_button.size['width']
        
        # 手機上按鈕應該有足夠的觸控區域
        self.assertGreaterEqual(button_height, 70)  # 至少 70px 高度
        self.assertGreater(button_width, 200)  # 寬度應該較大

    def test_mobile_game_controls_layout(self):
        """測試用例：手機版遊戲控制按鈕佈局"""
        self._login()
        
        # 等待遊戲控制按鈕出現
        game_controls = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "game-controls"))
        )
        buttons = game_controls.find_elements(By.TAG_NAME, "button")
        
        # 應該有至少 3 個按鈕（開始遊戲、商店、成就）
        self.assertGreaterEqual(len(buttons), 3)
        
        # 檢查按鈕是否可見
        time.sleep(0.3)
        for button in buttons:
            self.wait.until(EC.visibility_of(button))
            self.assertTrue(button.is_displayed())

    def test_mobile_statistics_display(self):
        """測試用例：手機版統計資訊顯示"""
        self._login()
        
        # 等待用戶資訊顯示
        self.wait.until(
            EC.presence_of_element_located((By.ID, "userInfo"))
        )
        time.sleep(0.3)
        self._handle_alert_if_present()
        
        # 等待統計資訊元素出現並可見
        coins_display = self.wait.until(
            EC.visibility_of_element_located((By.ID, "coinsDisplay"))
        )
        total_clicks = self.wait.until(
            EC.visibility_of_element_located((By.ID, "totalClicksDisplay"))
        )
        best_clicks = self.wait.until(
            EC.visibility_of_element_located((By.ID, "bestClicksDisplay"))
        )
        
        # 檢查元素是否可見
        self.assertTrue(coins_display.is_displayed())
        self.assertTrue(total_clicks.is_displayed())
        self.assertTrue(best_clicks.is_displayed())

    def test_mobile_modal_responsive(self):
        """測試用例：手機版模態框響應式設計"""
        self._login()
        
        # 確保沒有 loading
        self._wait_for_loading_to_disappear()
        # 打開商店模態框
        shop_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '商店')]"))
        )
        # 使用 JavaScript 點擊，避免被其他元素遮擋
        self.driver.execute_script("arguments[0].click();", shop_button)
        # 等待 loading 消失
        self._wait_for_loading_to_disappear()
        time.sleep(0.3)
        self._handle_alert_if_present()
        
        # 等待模態框出現
        shop_modal = self.wait.until(
            EC.presence_of_element_located((By.ID, "shopModal"))
        )
        
        # 檢查模態框是否可見
        self.assertTrue(shop_modal.is_displayed())
        
        # 檢查模態框內容寬度（手機上應該適應螢幕）
        modal_content = shop_modal.find_element(By.CLASS_NAME, "modal-content")
        modal_width = modal_content.size['width']
        
        # 手機上模態框應該接近視窗寬度
        self.assertLessEqual(modal_width, 500)

    def test_mobile_badge_display(self):
        """測試用例：手機版徽章顯示"""
        self._login()
        
        # 檢查徽章容器
        badges_container = self.driver.find_element(By.CLASS_NAME, "badges-container-game")
        
        # 檢查徽章槽位
        badge_slots = badges_container.find_elements(By.CLASS_NAME, "badge-slot")
        self.assertEqual(len(badge_slots), 3)  # 應該有 3 個徽章槽位
        
        # 檢查徽章槽位大小（手機上應該較小）
        for slot in badge_slots:
            slot_size = slot.size
            self.assertLess(slot_size['width'], 50)
            self.assertLess(slot_size['height'], 50)

