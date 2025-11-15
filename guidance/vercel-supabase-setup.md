# Vercel + Supabase 設置指南

## 重要說明

**這是 Django 專案，不需要 Supabase JavaScript 客戶端庫！**

Supabase 提供的是標準的 PostgreSQL 資料庫，Django 可以直接使用 `psycopg2-binary` 連接，就像連接任何 PostgreSQL 資料庫一樣。

## 步驟 1: 在 Supabase 創建資料庫

1. 前往 https://supabase.com 註冊並登入
2. 創建新專案
3. 在專案設置中，前往 **Settings** → **Database**
4. 找到 **Connection string** 或 **Connection info**，記錄以下資訊：
   - **Host**: 例如 `xxx.supabase.co`
   - **Database name**: 通常是 `postgres`
   - **Port**: 通常是 `5432`
   - **User**: 通常是 `postgres`
   - **Password**: 在創建專案時設置的密碼

## 步驟 2: 在 Vercel 設置環境變數

在 Vercel 專案設置中，前往 **Settings** → **Environment Variables**，添加以下變數：

### 方法 A: 使用 Session Pooler（推薦，必須用於 Vercel）

**⚠️ 重要**：Supabase 的 Direct Connection 只支援 IPv6，Vercel 使用 IPv4，會導致 "Cannot assign requested address" 錯誤。**必須使用 Session Pooler** 來解決 IPv4 相容性問題。

1. 在 Supabase 專案中，前往 **Settings** → **Database**
2. 找到 **Connection string** 區塊
3. 選擇 **URI** 格式
4. **關鍵步驟**：在 **Method** 下拉選單中，選擇 **Session Pooler**（不是 Direct connection）
5. 複製 Session Pooler 的連接字串（格式：`postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-xx.pooler.supabase.com:6543/postgres`）
   - 注意：Session Pooler 的主機地址是 `aws-0-xx.pooler.supabase.com`，端口是 `6543`（不是 5432）
   - 用戶名格式是 `postgres.xxxxx`（不是 `postgres`）
6. 將 `[YOUR-PASSWORD]` 替換為實際密碼
7. 在 Vercel 中設置環境變數：
   ```
   DATABASE_URL=postgresql://postgres.xxxxx:你的密碼@aws-0-xx.pooler.supabase.com:6543/postgres
   VERCEL=1
   ```

**Session Pooler vs Direct Connection**：
- **Session Pooler**（推薦）：✅ 支援 IPv4，適合 Vercel、Heroku 等平台，端口 `6543`
- **Direct Connection**（不適用於 Vercel）：❌ 只支援 IPv6，端口 `5432`，會導致 "Cannot assign requested address" 錯誤

### 方法 B: 使用個別環境變數（備選方案）

如果不想使用 `DATABASE_URL`，也可以設置個別變數：

```
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=你的 Supabase 密碼
DB_HOST=你的專案.supabase.co
DB_PORT=5432
VERCEL=1
```

**重要**：
- 確保這些變數設置在 **Production**、**Preview** 和 **Development** 環境中
- `DATABASE_URL` 的優先級高於個別環境變數
- 如果同時設置了 `DATABASE_URL` 和個別變數，系統會優先使用 `DATABASE_URL`

## 步驟 2.5: 設置 Vercel Function Region（優化響應時間）

**⚡ 性能優化建議**：選擇接近 Supabase 伺服器位置的 Vercel Function Region，可以顯著減少 API 響應時間。

### 如何找到 Supabase 的區域位置

1. 前往 Supabase 專案 → **Settings** → **General**
2. 查看 **Region** 欄位，會顯示 Supabase 專案的區域（例如：`Southeast Asia (Singapore)`、`US East (North Virginia)` 等）

### 如何設置 Vercel Function Region

#### 方法 A: 在 Vercel Dashboard 設置（推薦）

1. 前往 Vercel 專案 → **Settings** → **Functions**
2. 找到 **Function Region** 設置
3. 選擇最接近 Supabase 區域的 Vercel 區域：
   - **Supabase 區域對應建議**：
     - `Southeast Asia (Singapore)` → `sin1` (Singapore)
     - `US East (North Virginia)` → `iad1` (Washington, D.C.)
     - `US West (Oregon)` → `sfo1` (San Francisco)
     - `EU West (Ireland)` → `dub1` (Dublin)
     - `EU Central (Frankfurt)` → `fra1` (Frankfurt)
     - `Asia Pacific (Tokyo)` → `hnd1` (Tokyo)
     - `Asia Pacific (Sydney)` → `syd1` (Sydney)
     - `South America (São Paulo)` → `gru1` (São Paulo)

#### 方法 B: 在 vercel.json 中設置

在 `vercel.json` 中添加 `regions` 配置：

```json
{
  "builds": [
    {
      "src": "react_game/wsgi.py",
      "use": "@vercel/python",
      "config": { 
        "maxLambdaSize": "15mb", 
        "runtime": "python3.9",
        "buildCommand": "python manage.py migrate && python manage.py init_game_data",
        "regions": ["sin1"]
      }
    }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "react_game/wsgi.py" }
  ]
}
```

**注意**：
- 將 `"sin1"` 替換為對應的區域代碼（見上方對應表）
- 可以設置多個區域以實現容錯，但建議只設置一個最接近的區域以獲得最佳性能
- 如果同時在 Dashboard 和 `vercel.json` 中設置，`vercel.json` 的設置會優先

### 性能影響

選擇正確的 Function Region 可以：
- ✅ 減少資料庫查詢延遲（通常可減少 50-200ms）
- ✅ 提升 API 響應速度
- ✅ 改善用戶體驗，特別是對於資料庫密集型操作

**建議**：如果您的 Supabase 專案在 `Southeast Asia (Singapore)`，將 Vercel Function Region 設置為 `sin1`，可以將 API 響應時間從 2-3 秒降低到 1 秒左右。

## 步驟 3: 執行資料庫遷移

資料庫遷移已經在 `vercel.json` 中配置，會在每次部署時自動執行。

**注意**：由於 `vercel.json` 中有 `builds` 配置，Vercel 會忽略 Project Settings 中的 Build Command，改為使用 `vercel.json` 中定義的 `buildCommand`。

### 自動執行（已配置）

`vercel.json` 中已經包含以下配置：

```json
{
  "builds": [
    {
      "config": {
        "buildCommand": "python manage.py migrate && python manage.py init_game_data"
      }
    }
  ]
}
```

這會在每次部署時自動執行資料庫遷移和初始化遊戲資料。

### 手動執行（首次部署或故障排除）

如果需要手動執行遷移，可以：

1. 在本地連接到 Supabase 資料庫執行遷移
2. 或使用 Supabase SQL Editor 手動執行

## 步驟 4: 重新部署

1. 提交所有變更到 Git 倉庫
2. 推送到遠端（GitHub/GitLab 等）
3. Vercel 會自動觸發新的部署
4. 或在 Vercel 專案頁面手動點擊 **Redeploy**

## 步驟 5: 驗證連接

部署完成後，訪問您的應用程式。如果看到遊戲界面正常顯示，表示資料庫連接成功。

## 本地開發設置（可選）

如果您想在本地開發時也使用 Supabase，創建 `.env.local` 文件（不要提交到 Git）：

```bash
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=你的 Supabase 密碼
DB_HOST=你的專案.supabase.co
DB_PORT=5432
```

然後在本地執行：

```bash
python manage.py migrate
python manage.py init_game_data
```

## 故障排除

### 🔍 系統化診斷步驟

如果連接失敗，請按照以下步驟逐一檢查：

#### 步驟 1: 檢查 Vercel 環境變數

1. 前往 Vercel 專案 → **Settings** → **Environment Variables**
2. 確認以下變數已設置：
   - `DATABASE_URL` 或（`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`）
   - `VERCEL=1`
3. **重要**：確認變數設置在正確的環境中（Production、Preview、Development）
4. 檢查 `DATABASE_URL` 格式是否正確：
   ```
   postgresql://postgres:密碼@主機:5432/postgres
   ```
5. 如果使用 `DATABASE_URL`，確認密碼中的特殊字元已正確 URL 編碼：
   - `@` → `%40`
   - `:` → `%3A`
   - `/` → `%2F`
   - `#` → `%23`
   - `%` → `%25`

#### 步驟 2: 檢查 Vercel 部署日誌

1. 前往 Vercel 專案 → **Deployments**
2. 點擊最新的部署記錄
3. 查看 **Build Logs** 和 **Function Logs**
4. 尋找以下錯誤訊息：
   - `could not connect to server`
   - `authentication failed`
   - `database does not exist`
   - `SSL connection required`

#### 步驟 3: 驗證 Supabase 連接資訊

1. 前往 Supabase 專案 → **Settings** → **Database**
2. 確認 **Connection string** 中的資訊：
   - **Host**: 應該是 `db.xxxxx.supabase.co`（不是 `xxx.supabase.co`）
   - **Database**: 應該是 `postgres`
   - **Port**: 應該是 `5432`
   - **User**: 應該是 `postgres`
   - **Password**: 確認密碼正確
3. 測試連接字串：
   - 複製 Supabase 提供的 **URI** 格式連接字串
   - 確認格式為：`postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`

#### 步驟 4: 檢查 Supabase 專案狀態

1. 確認 Supabase 專案狀態為 **Active**（不是暫停或刪除）
2. 檢查專案的 **Database** 頁面，確認資料庫正常運行
3. 查看 **Logs** 頁面，檢查是否有連接錯誤記錄

#### 步驟 5: 本地測試連接（可選）

在本地環境測試連接，確認 Supabase 連接資訊正確：

**重要提示**：如果本地網路無法連接到 Supabase（DNS 解析失敗或 IPv6 問題），這不影響 Vercel 部署。Vercel 的網路環境通常可以正常連接。

##### 方法 A: 標準連接測試

1. **安裝依賴**（如果尚未安裝）：
   ```bash
   pip install python-dotenv
   ```
   或安裝所有依賴：
   ```bash
   pip install -r requirements.txt
   ```

2. **創建 `.env.local` 文件**（在專案根目錄，不會提交到 Git）：
   ```bash
   DATABASE_URL=postgresql://postgres:你的密碼@db.xxxxx.supabase.co:5432/postgres
   ```
   
   **重要**：
   - 將 `你的密碼` 替換為 Supabase 的實際密碼
   - 將 `db.xxxxx.supabase.co` 替換為實際的主機地址
   - 如果密碼包含特殊字元，需要進行 URL 編碼

3. **在本地執行測試**：
   ```bash
   python manage.py migrate
   python manage.py init_game_data
   ```

4. **判斷結果**：
   - ✅ 如果本地連接成功，問題可能在 Vercel 環境變數設置
   - ❌ 如果本地也失敗，可能是網路限制（不影響 Vercel 部署）

##### 方法 B: 如果本地無法連接（網路限制）

如果本地無法連接到 Supabase（DNS 解析失敗或 IPv6 問題），可以：

1. **使用 VPN 或代理**：連接到可以訪問 Supabase 的網路
2. **直接測試 Vercel 部署**：本地連接失敗不影響 Vercel 部署，可以直接在 Vercel 上測試
3. **使用 Supabase Studio**：在 Supabase Dashboard 的 SQL Editor 中直接執行 SQL 命令進行測試

##### 方法 C: 本地開發使用 SQLite（僅開發環境）

如果本地開發需要，可以暫時使用 SQLite：

1. **在 `.env.local` 中添加**：
   ```bash
   USE_SQLITE=true
   ```

2. **這樣配置**：
   - 本地開發：使用 SQLite3（`db.sqlite3`）
   - Vercel 部署：使用 Supabase PostgreSQL（透過 `DATABASE_URL`）

**注意**：本地使用 SQLite 和 Vercel 使用 PostgreSQL 的資料是分開的，僅用於開發測試。

##### 測試完成後

- 可以刪除 `.env.local` 文件，或保留用於本地開發
- 確認 `.env.local` 已在 `.gitignore` 中（已配置）

#### 步驟 6: 檢查 SSL 配置

1. 確認 Supabase 的 SSL 設置：
   - 前往 **Settings** → **Database** → **SSL Configuration**
   - 確認 "Enforce SSL on incoming connections" 已啟用
2. Django 配置已自動設置 `sslmode: 'require'`，無需額外配置

#### 步驟 7: 檢查 Supabase 連接限制

1. 前往 **Settings** → **Database** → **Connection Pooling**
2. 確認連接數未超過限制（免費方案通常有連接數限制）
3. 檢查是否有其他應用程式佔用過多連接

### 常見錯誤訊息及解決方案

#### 錯誤：`could not connect to server` 或 `Cannot assign requested address`

**可能原因**：
- `DB_HOST` 或 `DATABASE_URL` 中的主機地址錯誤
- Supabase 專案已暫停或刪除
- 網路連接問題
- **IPv4/IPv6 不相容問題**（最常見）

**解決方案**：
1. **檢查是否使用 Session Pooler**：
   - 如果使用 Direct Connection（端口 5432），可能無法在 Vercel 上使用
   - 改用 Session Pooler（端口 6543），支援 IPv4
   - 在 Supabase Dashboard → Settings → Database → Connection string → Method 選擇 "Session Pooler"

2. 確認 Supabase 主機地址格式：
   - Direct Connection：`db.xxxxx.supabase.co:5432`
   - Session Pooler：`aws-0-xx.pooler.supabase.com:6543`

3. 確認 Supabase 專案狀態為 Active

4. 檢查 Vercel 部署日誌中的完整錯誤訊息

5. **如果錯誤訊息包含 "Cannot assign requested address"**：
   - 這通常是 IPv4/IPv6 不相容問題
   - 必須使用 Session Pooler 而不是 Direct Connection

#### 錯誤：`authentication failed for user "postgres"`

**可能原因**：
- 密碼錯誤
- 密碼中的特殊字元未正確 URL 編碼

**解決方案**：
1. 在 Supabase 中重置資料庫密碼（**Settings** → **Database** → **Database Password**）
2. 更新 Vercel 環境變數中的密碼
3. 如果使用 `DATABASE_URL`，確保特殊字元已正確編碼

#### 錯誤：`database "xxx" does not exist`

**可能原因**：
- `DB_NAME` 或 `DATABASE_URL` 中的資料庫名稱錯誤

**解決方案**：
1. Supabase 預設資料庫名稱是 `postgres`，不是 `clickfast_db`
2. 確認 `DATABASE_URL` 中的資料庫名稱：`postgresql://.../postgres`

#### 錯誤：`SSL connection required`

**可能原因**：
- Supabase 強制要求 SSL，但連接未使用 SSL

**解決方案**：
1. 確認 `settings.py` 中的 `sslmode: 'require'` 已設置（已完成）
2. 如果仍有問題，嘗試使用 `sslmode: 'prefer'`（不推薦，安全性較低）

#### 錯誤：`connection timeout`

**可能原因**：
- 網路連接問題
- Supabase 專案暫停（免費方案會自動暫停）

**解決方案**：
1. 確認 Supabase 專案狀態為 Active
2. 如果專案已暫停，前往 Supabase Dashboard 重新啟動
3. 檢查 Vercel 的網路連接

### 進階診斷：添加調試日誌

如果需要更詳細的錯誤訊息，可以在 `settings.py` 中臨時添加調試日誌：

```python
import logging

# 在資料庫配置後添加
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

**注意**：調試完成後請移除此配置，避免在生產環境中暴露敏感資訊。

## SSL 連接配置

Supabase 預設啟用 SSL 連接。Django 配置已自動設置 `sslmode: 'require'`，確保所有資料庫連接都使用 SSL。

**重要**：
- 如果 Supabase 的 SSL 設置為「Enforce SSL on incoming connections」，Django 會自動使用 SSL 連接
- 不需要下載或配置 SSL 證書
- 所有 PostgreSQL 連接都會自動使用 SSL

## 注意事項

1. **不要**在代碼中硬編碼資料庫密碼
2. **不要**將 `.env.local` 提交到 Git（已在 `.gitignore` 中）
3. Supabase 免費方案有連接數限制，適合小型專案
4. 生產環境建議使用強密碼並定期更換
5. SSL 連接已自動配置，無需額外設置

