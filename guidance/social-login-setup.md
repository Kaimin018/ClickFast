# 社交登入設定指南

本專案已整合 Google、Facebook 和 Instagram 社交登入功能，使用 `django-allauth` 套件實現。

## 安裝依賴

已更新 `requirements.txt`，包含 `django-allauth==0.57.0`。

執行以下命令安裝：

```bash
pip install -r requirements.txt
```

## 資料庫遷移

首次使用需要執行資料庫遷移：

```bash
python manage.py migrate
```

這會創建 allauth 所需的資料表。

## 配置社交登入應用

### 方法一：使用管理命令（推薦，最快速）

執行以下命令自動配置社交登入應用：

```bash
# Windows PowerShell（需要設置 UTF-8 編碼）
$env:PYTHONIOENCODING="utf-8"
python manage.py setup_social_login
```

這會自動：
- 創建或更新 Site（127.0.0.1:8000）
- 創建 Google、Facebook、Instagram 社交應用
- 將應用添加到 Site

**注意**：此命令會使用預設的 Client ID 和 Secret（需要更新）。要使用真實憑證，請：

1. **從環境變數讀取**（推薦）：
```bash
# 設置環境變數後執行
$env:PYTHONIOENCODING="utf-8"
python manage.py setup_social_login --use-env
```

2. **或在 Django Admin 中手動更新**：
   - 訪問 http://127.0.0.1:8000/admin/
   - 進入「Social applications」
   - 編輯每個應用，更新 Client ID 和 Secret

### 方法二：使用 Django Admin（手動配置）

1. 創建超級用戶（如果還沒有）：
```bash
python manage.py createsuperuser
```

2. 啟動開發伺服器：
```bash
python manage.py runserver
```

3. 登入 Django Admin（http://127.0.0.1:8000/admin/）

4. 在「Sites」中確保有一個 Site 記錄，Domain 設為 `127.0.0.1:8000`（開發環境）或您的生產域名

5. 在「Social applications」中為每個提供者創建應用：
   - 點擊「Add social application」
   - 選擇 Provider（Google、Facebook 或 Instagram）
   - 輸入 Client id 和 Secret key（從各平台獲取）
   - 選擇 Sites（將應用添加到當前站點）

### 方法二：使用環境變數（需要額外配置）

在 `.env.local` 文件中添加以下環境變數：

```
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FACEBOOK_CLIENT_ID=your_facebook_app_id
FACEBOOK_CLIENT_SECRET=your_facebook_app_secret
INSTAGRAM_CLIENT_ID=your_instagram_client_id
INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret
```

**注意**：使用環境變數方式需要修改 `settings.py` 中的 `SOCIALACCOUNT_PROVIDERS` 配置，並在 Django Admin 中手動創建 Social Application 記錄。

## 獲取 OAuth 憑證

### Google OAuth

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 創建新專案或選擇現有專案
3. 啟用 Google+ API
4. 前往「憑證」頁面，創建 OAuth 2.0 客戶端 ID
5. 設定授權的重新導向 URI：
   - 開發環境：`http://127.0.0.1:8000/accounts/google/login/callback/`
   - 生產環境：`https://yourdomain.com/accounts/google/login/callback/`
6. 複製 Client ID 和 Client Secret

### Facebook OAuth

1. 前往 [Facebook Developers](https://developers.facebook.com/)
2. 創建新應用
3. 添加「Facebook 登入」產品
4. 在「設定」>「基本」中設定：
   - 應用程式網域
   - 網站網址
   - 有效的 OAuth 重新導向 URI：`http://127.0.0.1:8000/accounts/facebook/login/callback/`
5. 複製 App ID 和 App Secret

### Instagram OAuth

1. 前往 [Facebook Developers](https://developers.facebook.com/)
2. 創建新應用（選擇「消費者」類型）
3. 添加「Instagram 基本顯示」產品
4. 在「Instagram 基本顯示」設定中：
   - 設定有效的 OAuth 重新導向 URI：`http://127.0.0.1:8000/accounts/instagram/login/callback/`
5. 複製 App ID 和 App Secret

## 測試社交登入

1. 啟動開發伺服器
2. 訪問首頁
3. 點擊社交登入按鈕（Google、Facebook 或 Instagram）
4. 完成 OAuth 授權流程
5. 系統會自動創建用戶帳號並登入

## 注意事項

- 社交登入的用戶會自動創建 `PlayerProfile` 資料
- 用戶名會從社交帳號資訊中自動生成
- 如果社交帳號沒有提供用戶名，系統會使用社交帳號的 ID 或 email 作為用戶名
- 生產環境部署時，請確保在 OAuth 提供者平台中設定正確的回調 URL

## 故障排除

### 問題：社交登入後沒有自動登入

**解決方案**：
1. 檢查 Django Admin 中的 Site 設定是否正確
2. 確認 Social Application 已正確配置並添加到當前 Site
3. 檢查瀏覽器控制台是否有錯誤訊息

### 問題：OAuth 回調失敗

**解決方案**：
1. 確認 OAuth 提供者平台中的回調 URL 設定正確
2. 檢查 `ALLOWED_HOSTS` 設定是否包含您的域名
3. 確認 Client ID 和 Secret 正確無誤

### 問題：Instagram 登入無法使用

**注意**：Instagram 的 OAuth 功能可能需要特殊權限或審核，請參考 [Instagram Basic Display API 文檔](https://developers.facebook.com/docs/instagram-basic-display-api)

