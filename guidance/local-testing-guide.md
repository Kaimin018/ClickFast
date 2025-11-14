# ClickFast 本地測試指南

## 快速開始

### 1. 啟動虛擬環境

在 PowerShell 中執行：

```powershell
cd "D:\2025 coding project\09_ClickFast"
myenv\Scripts\activate
```

如果虛擬環境未啟動，命令提示符前會顯示 `(myenv)`。

### 2. 安裝依賴（如果需要）

如果還沒有安裝依賴，執行：

```powershell
pip install -r requirements.txt
```

### 3. 建立資料庫遷移

首次執行或模型有變更時，需要建立遷移：

```powershell
python manage.py makemigrations
```

### 4. 執行資料庫遷移

將遷移應用到資料庫：

```powershell
python manage.py migrate
```

### 5. 初始化遊戲資料

初始化商店物品和成就資料（注意：需要設定 UTF-8 編碼以避免中文顯示問題）：

```powershell
$env:PYTHONIOENCODING="utf-8"
python manage.py init_game_data
```

這將建立：
- 3種商店物品（遊戲時間延長、額外點擊按鈕、自動點擊器）
- 9個成就（總點擊、單局點擊、遊戲局數等）

### 6. 啟動開發伺服器

```powershell
python manage.py runserver
```

伺服器啟動後，你會看到類似以下輸出：

```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### 7. 存取遊戲

在瀏覽器中開啟：

- **遊戲主頁**: http://127.0.0.1:8000/
- **Django 管理後台**: http://127.0.0.1:8000/admin/ （需要先建立超級使用者）

## 建立超級使用者（可選）

如果需要存取 Django 管理後台來檢視和管理資料：

```powershell
python manage.py createsuperuser
```

然後按照提示輸入使用者名稱、電子郵件和密碼。

## 建立超級測試帳號（可選）

用於測試成就系統和商店物品功能：

```powershell
python manage.py create_super_account
```

或者指定使用者名稱和金幣數量：

```powershell
python manage.py create_super_account --username test_user --coins 2000000
```

超級帳號將自動：
- 擁有大量金幣（預設 1,000,000）
- 購買所有商店物品到最高等級
- 解鎖所有成就（獎勵已自動領取）
- 擁有高額的遊戲統計數據（總點擊50000、單局最佳500、遊戲局數200、對戰勝場50）

## 測試步驟

1. **開啟遊戲主頁**: 存取 http://127.0.0.1:8000/
2. **登入/註冊**: 輸入使用者名稱開始遊戲（首次輸入會自動建立使用者）
3. **開始遊戲**: 點擊"開始遊戲"按鈕，在10秒內盡可能多地點擊
4. **測試商店**: 賺取金幣後，在商店購買升級物品
5. **測試成就**: 完成各種挑戰解鎖成就
6. **檢視歷史**: 檢視遊戲歷史記錄

## 常見問題

### 問題：埠 8000 已被佔用

解決方案：使用其他埠

```powershell
python manage.py runserver 8001
```

然後存取 http://127.0.0.1:8001/

### 問題：資料庫錯誤

解決方案：刪除 `db.sqlite3` 檔案，然後重新執行遷移

```powershell
# 刪除資料庫檔案
Remove-Item db.sqlite3

# 重新建立遷移
python manage.py makemigrations
python manage.py migrate
python manage.py init_game_data
```

### 問題：模組匯入錯誤

解決方案：確保虛擬環境已啟動，並且已安裝所有依賴

```powershell
# 檢查虛擬環境
# 命令提示符前應該有 (myenv)

# 重新安裝依賴
pip install -r requirements.txt
```

## 停止伺服器

在執行伺服器的終端視窗中，按 `Ctrl + C` 停止伺服器。

## 完整測試流程（一次性命令）

如果你想一次性執行所有設定步驟：

```powershell
# 1. 進入專案目錄
cd "D:\2025 coding project\09_ClickFast"

# 2. 啟動虛擬環境
myenv\Scripts\activate

# 3. 安裝依賴（如果需要）
pip install -r requirements.txt

# 4. 建立遷移
python manage.py makemigrations

# 5. 執行遷移
python manage.py migrate

# 6. 初始化遊戲資料（設定 UTF-8 編碼）
$env:PYTHONIOENCODING="utf-8"
python manage.py init_game_data

# 7. （可選）建立超級測試帳號
python manage.py create_super_account

# 8. 啟動伺服器
python manage.py runserver
```

然後開啟瀏覽器存取 http://127.0.0.1:8000/ 開始測試！


