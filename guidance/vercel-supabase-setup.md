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

```
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=你的 Supabase 密碼
DB_HOST=你的專案.supabase.co
DB_PORT=5432
VERCEL=1
```

**重要**：確保這些變數設置在 **Production**、**Preview** 和 **Development** 環境中。

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

### 問題：連接被拒絕

- 檢查 `DB_HOST` 是否正確（應該是 `xxx.supabase.co`，不是 `localhost`）
- 檢查 Supabase 專案的防火牆設置，確保允許外部連接
- 檢查密碼是否正確

### 問題：認證失敗

- 確認 `DB_USER` 和 `DB_PASSWORD` 正確
- 檢查 Supabase 專案設置中的資料庫用戶資訊

### 問題：資料庫不存在

- 確認 `DB_NAME` 正確（Supabase 預設是 `postgres`）
- 檢查 Supabase 專案是否已正確創建

## 注意事項

1. **不要**在代碼中硬編碼資料庫密碼
2. **不要**將 `.env.local` 提交到 Git（已在 `.gitignore` 中）
3. Supabase 免費方案有連接數限制，適合小型專案
4. 生產環境建議使用強密碼並定期更換

