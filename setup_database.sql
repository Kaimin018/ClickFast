-- ClickFast 資料庫設置腳本
-- 適用於 PostgreSQL

-- ============================================
-- 步驟 1: 創建資料庫
-- ============================================
-- 連接到 PostgreSQL 後執行以下命令：
-- CREATE DATABASE clickfast_db;

-- 設置字符編碼（可選，但建議）
-- ALTER DATABASE clickfast_db SET encoding = 'UTF8';

-- ============================================
-- 步驟 2: 創建用戶（可選，用於生產環境）
-- ============================================
-- CREATE USER clickfast_user WITH PASSWORD 'your_password_here';
-- GRANT ALL PRIVILEGES ON DATABASE clickfast_db TO clickfast_user;

-- ============================================
-- 步驟 3: 設置環境變數
-- ============================================
-- 在部署平台或本地環境中設置以下環境變數：
-- DB_NAME=clickfast_db
-- DB_USER=clickfast_user (或 postgres)
-- DB_PASSWORD=your_password_here
-- DB_HOST=localhost (或資料庫主機地址)
-- DB_PORT=5432

-- ============================================
-- 步驟 4: 執行 Django 遷移
-- ============================================
-- 連接到資料庫後，執行以下命令：
-- python manage.py migrate
-- python manage.py init_game_data

-- ============================================
-- 注意事項
-- ============================================
-- 1. 請將 'your_password_here' 替換為實際的強密碼
-- 2. 生產環境請使用強密碼並妥善保管
-- 3. 建議使用環境變數管理資料庫連接資訊，不要硬編碼在代碼中
-- 4. 本地開發可以使用 SQLite3（設置環境變數 USE_SQLITE=true）
-- 5. 生產環境必須使用 PostgreSQL

