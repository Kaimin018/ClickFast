"""
UI系統測試 - 頁面載入
TC_UI_001: 頁面成功載入測試
"""
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class PageLoadTestCase(LiveServerTestCase):
    """頁面載入測試類"""

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

    def test_page_loads_successfully(self):
        """測試用例：頁面成功載入"""
        self.driver.get(self.live_server_url)
        
        # 檢查頁面標題
        self.assertIn("ClickFast", self.driver.title)
        
        # 檢查主要元素是否存在
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertIsNotNone(body)

