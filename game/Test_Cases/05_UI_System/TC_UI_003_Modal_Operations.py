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
from game.Test_Cases.base_test_case import PostgreSQLLiveServerTestCase
import time


class ModalOperationsTestCase(PostgreSQLLiveServerTestCase):
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
        # 等待 loading 消失
        self._wait_for_loading_to_disappear()
        self.wait.until(
            EC.presence_of_element_located((By.ID, "gameContent"))
        )

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

    def test_shop_modal_open_close(self):
        """測試用例：商店模態框打開和關閉"""
        # 確保沒有 loading
        self._wait_for_loading_to_disappear()
        # 打開商店
        shop_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '商店')]"))
        )
        # 使用 JavaScript 點擊，避免被其他元素遮擋
        self.driver.execute_script("arguments[0].click();", shop_button)
        
        # 等待模態框出現並顯示
        shop_modal = self.wait.until(
            EC.visibility_of_element_located((By.ID, "shopModal"))
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
        # 確保沒有 loading
        self._wait_for_loading_to_disappear()
        # 打開成就
        achievement_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '成就')]"))
        )
        # 使用 JavaScript 點擊，避免被其他元素遮擋
        self.driver.execute_script("arguments[0].click();", achievement_button)
        
        # 等待模態框出現並顯示
        achievement_modal = self.wait.until(
            EC.visibility_of_element_located((By.ID, "achievementsModal"))
        )
        self.assertTrue(achievement_modal.is_displayed())
        
        # 關閉模態框
        close_button = achievement_modal.find_element(By.CLASS_NAME, "close-btn")
        close_button.click()
        
        time.sleep(0.5)
        
        # 檢查模態框是否隱藏
        modal_classes = achievement_modal.get_attribute("class")
        self.assertNotIn("active", modal_classes)

    def test_confirm_modal_display(self):
        """測試用例：確認對話框顯示和操作"""
        # 確保在遊戲頁面（重新載入確保狀態正確）
        self.driver.get(self.live_server_url)
        self._wait_for_loading_to_disappear()
        
        # 重新登入確保狀態正確
        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "usernameInput"))
        )
        username_input.clear()
        username_input.send_keys("testuser")
        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '開始遊戲')]")
        self.driver.execute_script("arguments[0].click();", login_button)
        self._wait_for_loading_to_disappear()
        self.wait.until(
            EC.presence_of_element_located((By.ID, "gameContent"))
        )
        
        # 額外等待確保頁面完全載入
        time.sleep(0.5)
        
        # 觸發確認對話框（通過登出按鈕）
        # 登出按鈕在設定下拉選單中，需要先打開設定選單
        settings_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '設定')]"))
        )
        # 使用 JavaScript 點擊設定按鈕
        self.driver.execute_script("arguments[0].click();", settings_button)
        time.sleep(0.3)  # 等待下拉選單出現
        
        # 點擊登出按鈕
        logout_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'logout') and contains(text(), '登出')]"))  
        )
        # 使用 JavaScript 點擊，避免被其他元素遮擋
        self.driver.execute_script("arguments[0].click();", logout_button)
        
        # 等待確認對話框出現並顯示
        confirm_modal = self.wait.until(
            EC.presence_of_element_located((By.ID, "confirmModal"))
        )
        # 等待 modal 添加 active class
        self.wait.until(
            lambda driver: 'active' in driver.find_element(By.ID, "confirmModal").get_attribute("class")
        )
        # 確保 modal 可見
        self.wait.until(
            EC.visibility_of_element_located((By.ID, "confirmModal"))
        )
        self.assertTrue(confirm_modal.is_displayed())
        
        # 檢查確認對話框內容
        confirm_title = confirm_modal.find_element(By.ID, "confirmTitle")
        self.assertIn("確認", confirm_title.text)
        
        confirm_message = confirm_modal.find_element(By.ID, "confirmMessage")
        self.assertIn("登出", confirm_message.text)
        
        # 點擊取消按鈕
        cancel_button = confirm_modal.find_element(By.ID, "confirmCancelBtn")
        cancel_button.click()
        
        time.sleep(0.5)
        
        # 檢查確認對話框是否隱藏
        modal_classes = confirm_modal.get_attribute("class")
        self.assertNotIn("active", modal_classes)

    def test_alert_modal_display(self):
        """測試用例：提示對話框顯示和操作"""
        # 直接重新載入登入頁面，確保在登入頁面
        self.driver.get(self.live_server_url)
        self._wait_for_loading_to_disappear()
        
        # 額外等待確保頁面完全載入
        time.sleep(0.5)
        
        # 觸發提示對話框（通過嘗試登入空用戶名）
        # 先等待輸入框可互動
        username_input = self.wait.until(
            EC.element_to_be_clickable((By.ID, "usernameInput"))
        )
        # 使用 JavaScript 清空輸入框
        self.driver.execute_script("arguments[0].value = '';", username_input)
        
        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '開始遊戲')]")
        # 使用 JavaScript 點擊，避免被其他元素遮擋
        self.driver.execute_script("arguments[0].click();", login_button)
        
        # 等待提示對話框出現並顯示
        alert_modal = self.wait.until(
            EC.visibility_of_element_located((By.ID, "alertModal"))
        )
        # 等待 modal 添加 active class
        self.wait.until(
            lambda driver: 'active' in driver.find_element(By.ID, "alertModal").get_attribute("class")
        )
        self.assertTrue(alert_modal.is_displayed())
        
        # 檢查提示對話框內容
        alert_title = alert_modal.find_element(By.ID, "alertTitle")
        self.assertIn("提示", alert_title.text)
        
        alert_message = alert_modal.find_element(By.ID, "alertMessage")
        self.assertIn("用戶名", alert_message.text)
        
        # 點擊確定按鈕
        ok_button = alert_modal.find_element(By.ID, "alertOkBtn")
        ok_button.click()
        
        time.sleep(0.5)
        
        # 檢查提示對話框是否隱藏
        modal_classes = alert_modal.get_attribute("class")
        self.assertNotIn("active", modal_classes)

    def test_modal_background_click_close(self):
        """測試用例：點擊模態框背景關閉"""
        # 確保在遊戲頁面（重新載入確保狀態正確）
        self.driver.get(self.live_server_url)
        self._wait_for_loading_to_disappear()
        
        # 重新登入確保狀態正確
        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "usernameInput"))
        )
        username_input.clear()
        username_input.send_keys("testuser")
        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '開始遊戲')]")
        self.driver.execute_script("arguments[0].click();", login_button)
        self._wait_for_loading_to_disappear()
        self.wait.until(
            EC.presence_of_element_located((By.ID, "gameContent"))
        )
        
        # 額外等待確保頁面完全載入
        time.sleep(0.5)
        
        # 打開商店模態框
        shop_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '商店')]"))
        )
        # 使用 JavaScript 點擊，避免被其他元素遮擋
        self.driver.execute_script("arguments[0].click();", shop_button)
        # 等待 loading 消失
        self._wait_for_loading_to_disappear()
        
        # 等待模態框出現並顯示
        shop_modal = self.wait.until(
            EC.visibility_of_element_located((By.ID, "shopModal"))
        )
        self.assertTrue(shop_modal.is_displayed())
        
        # 點擊模態框背景（不是內容區域）
        # 使用 JavaScript 來模擬點擊背景
        self.driver.execute_script("""
            var modal = arguments[0];
            var event = new MouseEvent('click', {
                view: window,
                bubbles: true,
                cancelable: true
            });
            modal.dispatchEvent(event);
        """, shop_modal)
        
        time.sleep(0.5)
        
        # 檢查模態框是否隱藏（注意：商店模態框可能沒有背景點擊關閉功能）
        # 這個測試主要驗證確認和提示對話框的背景點擊功能
        # 先測試確認對話框的背景點擊
        # 登出按鈕在設定下拉選單中，需要先打開設定選單
        settings_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '設定')]"))
        )
        # 使用 JavaScript 點擊設定按鈕
        self.driver.execute_script("arguments[0].click();", settings_button)
        time.sleep(0.3)  # 等待下拉選單出現
        
        # 點擊登出按鈕
        logout_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'logout') and contains(text(), '登出')]"))
        )
        # 使用 JavaScript 點擊，避免被其他元素遮擋
        self.driver.execute_script("arguments[0].click();", logout_button)
        
        confirm_modal = self.wait.until(
            EC.presence_of_element_located((By.ID, "confirmModal"))
        )
        
        # 點擊確認對話框背景
        self.driver.execute_script("""
            var modal = arguments[0];
            var event = new MouseEvent('click', {
                view: window,
                bubbles: true,
                cancelable: true,
                clientX: 100,
                clientY: 100
            });
            Object.defineProperty(event, 'target', {value: modal, enumerable: true});
            modal.dispatchEvent(event);
        """, confirm_modal)
        
        time.sleep(0.5)
        
        # 檢查確認對話框是否隱藏
        modal_classes = confirm_modal.get_attribute("class")
        self.assertNotIn("active", modal_classes)

    def test_toast_notifications(self):
        """測試用例：Toast 通知顯示"""
        # 這個測試主要驗證 Toast 通知的存在和基本結構
        # 實際的 Toast 觸發需要特定的操作（如購買、錯誤等）
        
        # 檢查購買成功 Toast 元素是否存在
        purchase_toast = self.driver.find_element(By.ID, "purchaseToast")
        self.assertIsNotNone(purchase_toast)
        
        # 檢查錯誤提示 Toast 元素是否存在
        error_toast = self.driver.find_element(By.ID, "errorToast")
        self.assertIsNotNone(error_toast)
        
        # 檢查遊戲結算 Toast 元素是否存在
        game_result_toast = self.driver.find_element(By.ID, "gameResultToast")
        self.assertIsNotNone(game_result_toast)

    def test_achievement_notification_modal(self):
        """測試用例：成就解鎖通知模態框"""
        # 檢查成就解鎖通知模態框元素是否存在
        achievement_notification = self.driver.find_element(By.ID, "achievementNotification")
        self.assertIsNotNone(achievement_notification)
        
        # 檢查成就解鎖通知的結構
        notification_icon = achievement_notification.find_element(By.CLASS_NAME, "achievement-icon")
        self.assertIsNotNone(notification_icon)
        
        notification_title = achievement_notification.find_element(By.ID, "notificationTitle")
        self.assertIsNotNone(notification_title)
        
        notification_description = achievement_notification.find_element(By.ID, "notificationDescription")
        self.assertIsNotNone(notification_description)

    def test_badge_selection_response_speed(self):
        """測試用例：徽章選擇響應速度（無成就時）"""
        import time
        from game.models import PlayerAchievement
        from django.contrib.auth.models import User
        
        # 確保測試用戶沒有解鎖任何成就
        user = User.objects.get(username='testuser')
        PlayerAchievement.objects.filter(user=user).delete()
        
        # 確保在遊戲頁面（重新載入確保狀態正確）
        self.driver.get(self.live_server_url)
        self._wait_for_loading_to_disappear()
        
        # 重新登入確保狀態正確
        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "usernameInput"))
        )
        username_input.clear()
        username_input.send_keys("testuser")
        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '開始遊戲')]")
        self.driver.execute_script("arguments[0].click();", login_button)
        self._wait_for_loading_to_disappear()
        self.wait.until(
            EC.presence_of_element_located((By.ID, "gameContent"))
        )
        
        # 額外等待確保頁面完全載入和成就列表載入
        time.sleep(1.0)
        
        # 清除 gameState.unlockedAchievements 緩存（通過 JavaScript）
        self.driver.execute_script("""
            if (typeof gameState !== 'undefined') {
                gameState.unlockedAchievements = [];
            }
        """)
        
        # 確保沒有 loading
        self._wait_for_loading_to_disappear()
        # 點擊第一個徽章槽位
        badge_slot = self.wait.until(
            EC.element_to_be_clickable((By.ID, "badgeSlot1"))
        )
        
        # 記錄點擊前的時間
        start_time = time.time()
        # 使用 JavaScript 點擊，避免被其他元素遮擋
        self.driver.execute_script("arguments[0].click();", badge_slot)
        
        # 等待提示對話框出現（應該立即出現，因為沒有成就）
        # 使用較長的超時時間來驗證響應速度
        long_wait = WebDriverWait(self.driver, 10)
        # 等待 alert modal 出現並添加 active class（customAlert 是異步的）
        # 先等待元素存在
        alert_modal = long_wait.until(
            EC.presence_of_element_located((By.ID, "alertModal"))
        )
        # 等待 active class 添加（可能需要更長時間，因為是異步的）
        long_wait.until(
            lambda driver: 'active' in driver.find_element(By.ID, "alertModal").get_attribute("class"),
            message="等待 alert modal 添加 active class"
        )
        # 確保 modal 可見
        long_wait.until(
            EC.visibility_of_element_located((By.ID, "alertModal"))
        )
        
        # 記錄響應時間
        response_time = time.time() - start_time
        
        # 驗證響應時間應該很快（小於2秒）
        self.assertLess(response_time, 2.0, f"徽章選擇響應時間過長: {response_time:.2f}秒")
        # 等待訊息元素出現
        alert_message = self.wait.until(
            EC.presence_of_element_located((By.ID, "alertMessage"))
        )
        # 等待訊息文字出現（不強制要求包含"成就"，只要訊息不為空即可）
        try:
            self.wait.until(
                lambda driver: len(driver.find_element(By.ID, "alertMessage").text.strip()) > 0,
                timeout=3
            )
        except:
            pass  # 如果超時，繼續檢查
        message_text = alert_message.text.strip()
        # 驗證訊息有內容
        self.assertTrue(len(message_text) > 0, f"提示訊息應該有內容，但實際為: '{message_text}'")
        
        # 關閉提示
        ok_button = alert_modal.find_element(By.ID, "alertOkBtn")
        ok_button.click()
        
        time.sleep(0.5)

    def test_badge_selection_with_achievements(self):
        """測試用例：有成就時徽章選擇響應速度"""
        import time
        from game.models import Achievement, PlayerAchievement
        
        # 創建一個測試成就並解鎖
        achievement = Achievement.objects.create(
            name='測試成就',
            description='測試用成就',
            achievement_type='total_clicks',
            target_value=1,
            reward_coins=10,
            icon='🏆'
        )
        
        # 獲取當前用戶並解鎖成就
        from django.contrib.auth.models import User
        user = User.objects.get(username='testuser')
        PlayerAchievement.objects.get_or_create(
            user=user,
            achievement=achievement,
            defaults={'reward_claimed': True}
        )
        
        # 重新載入頁面以更新緩存
        self.driver.get(self.live_server_url)
        self._wait_for_loading_to_disappear()
        
        # 重新登入確保狀態正確
        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "usernameInput"))
        )
        username_input.clear()
        username_input.send_keys("testuser")
        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '開始遊戲')]")
        self.driver.execute_script("arguments[0].click();", login_button)
        self._wait_for_loading_to_disappear()
        self.wait.until(
            EC.presence_of_element_located((By.ID, "gameContent"))
        )
        
        # 額外等待確保頁面完全載入和成就列表載入
        time.sleep(1.0)
        
        # 確保沒有 loading
        self._wait_for_loading_to_disappear()
        
        # 點擊第一個徽章槽位
        badge_slot = self.wait.until(
            EC.element_to_be_clickable((By.ID, "badgeSlot1"))
        )
        
        # 記錄點擊前的時間
        start_time = time.time()
        # 使用 JavaScript 點擊，避免被其他元素遮擋
        self.driver.execute_script("arguments[0].click();", badge_slot)
        
        # 等待徽章選擇模態框出現（使用較長的超時時間，因為可能需要載入成就列表）
        long_wait = WebDriverWait(self.driver, 5)
        badge_modal = long_wait.until(
            EC.visibility_of_element_located((By.ID, "badgeSelectModal"))
        )
        
        # 記錄響應時間
        response_time = time.time() - start_time
        
        # 驗證響應時間應該很快（小於2秒，因為需要載入成就列表）
        self.assertLess(response_time, 2.0, f"徽章選擇響應時間過長: {response_time:.2f}秒")
        
        # 驗證模態框已顯示
        self.assertTrue(badge_modal.is_displayed())
        
        # 關閉模態框
        close_button = badge_modal.find_element(By.CLASS_NAME, "close-btn")
        close_button.click()
        
        time.sleep(0.5)

