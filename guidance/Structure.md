# ClickFast 專案結構說明

本文檔說明 ClickFast 專案的目錄結構和文件組織。


## game/ - 遊戲應用程式

主要的 Django 應用程式，包含遊戲邏輯、模型、視圖和模板。

```
game/
├── __init__.py              # Python 套件初始化
├── admin.py                 # Django 管理後台配置
├── apps.py                  # 應用程式配置
├── models.py                # 資料模型定義
├── views.py                 # 視圖函數（API 端點）
├── urls.py                  # URL 路由配置
├── tests.py                 # 測試文件（基本）
├── templates/               # HTML 模板目錄
│   └── game/
│       └── home.html        # 遊戲主頁面模板
├── migrations/              # 資料庫遷移文件
│   ├── __init__.py
│   └── 0001_initial.py      # 初始資料庫結構
├── management/              # Django 管理命令
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       ├── init_game_data.py  # 初始化遊戲資料命令
│       └── create_super_account.py  # 創建超級測試帳號命令
└── Test_Cases/              # 測試用例目錄
    ├── __init__.py
    └── test_case_01_game_flow.py  # 遊戲流程測試用例
```

### 主要文件說明

- **models.py**: 定義資料模型
  - `PlayerProfile`: 玩家資料（金幣、點擊數、遊戲局數等）
  - `GameSession`: 遊戲會話記錄
  - `ShopItem`: 商店物品
  - `PlayerPurchase`: 玩家購買記錄
  - `Achievement`: 成就定義
  - `PlayerAchievement`: 玩家成就解鎖記錄

- **views.py**: API 視圖函數
  - `home()`: 渲染遊戲主頁
  - `api_login_or_register()`: 登錄/註冊 API
  - `api_logout()`: 登出 API
  - `api_get_profile()`: 獲取玩家資料 API（包含購買記錄、成就、徽章）
  - `api_submit_game()`: 提交遊戲結果 API（自動檢查並解鎖成就）
  - `api_get_shop()`: 獲取商店物品 API
  - `api_purchase_item()`: 購買物品 API
  - `api_get_achievements()`: 獲取成就列表 API
  - `api_get_game_history()`: 獲取遊戲歷史 API
  - `api_update_badges()`: 更新用戶選擇的成就徽章 API

- **urls.py**: URL 路由配置
  - `/`: 遊戲主頁
  - `/api/login/`: 登錄/註冊
  - `/api/logout/`: 登出
  - `/api/profile/`: 獲取玩家資料
  - `/api/submit-game/`: 提交遊戲結果
  - `/api/shop/`: 商店相關
  - `/api/purchase/`: 購買物品
  - `/api/achievements/`: 成就相關
  - `/api/history/`: 歷史記錄
  - `/api/update-badges/`: 更新成就徽章

- **templates/game/home.html**: 遊戲前端頁面
  - 包含完整的 HTML、CSS 和 JavaScript
  - 遊戲邏輯、UI 互動、API 調用都在此文件中

## react_game/ - Django 專案設定

Django 專案的主要設定目錄。

```
react_game/
├── __init__.py              # Python 套件初始化
├── settings.py              # Django 設定檔
├── urls.py                  # 專案主 URL 配置
├── wsgi.py                  # WSGI 配置（用於部署）
└── asgi.py                  # ASGI 配置（用於異步部署）
```

### 主要文件說明

- **settings.py**: Django 專案設定
  - 資料庫配置（SQLite3，可配置為 PostgreSQL）
  - 已安裝的應用程式
  - 中間件配置
  - 靜態文件配置
  - 允許的主機設定

- **urls.py**: 專案主 URL 配置
  - 包含 `game` 應用的 URL 路由

## guidance/ - 文檔目錄

存放專案相關的文檔和指南。

```
guidance/
├── Structure.md             # 專案結構說明（本文件）
├── local-testing-guide.md   # 本地測試指南
├── How-to.md                # 開發和部署指南
└── NOTE.md                  # 部署平台備註
```

## assets/ - 靜態資源

存放圖片、截圖等靜態資源。

```
assets/
└── screenshot.png           # 遊戲截圖
```

## 資料庫結構

### PlayerProfile（玩家資料）
- `user`: 關聯到 Django User
- `coins`: 金幣數量
- `total_clicks`: 總點擊次數
- `best_clicks_per_round`: 單局最佳點擊數
- `total_games_played`: 總遊戲局數
- `battle_wins`: 對戰勝場數（預留功能）
- `badge_1_id`: 用戶選擇的第一個成就徽章 ID
- `badge_2_id`: 用戶選擇的第二個成就徽章 ID
- `badge_3_id`: 用戶選擇的第三個成就徽章 ID

### GameSession（遊戲記錄）
- `user`: 玩家
- `clicks`: 點擊次數
- `game_duration`: 遊戲時長（秒）
- `coins_earned`: 獲得金幣
- `played_at`: 遊戲時間

### ShopItem（商店物品）
- `name`: 物品名稱
- `item_type`: 物品類型（時間延長、額外按鈕、自動點擊器）
- `description`: 描述
- `base_price`: 基礎價格
- `effect_value`: 效果值
  - 時間延長：每次升級增加的秒數（預設 2 秒）
  - 額外按鈕：每次升級增加的按鈕數量（預設 1 個）
  - 自動點擊器：此值不再使用，頻率由等級直接計算
- `max_level`: 最大等級

**商店物品詳細說明：**
- **遊戲時間延長**：每次升級增加 2 秒遊戲時間（最高 10 級），延長時間內點擊獲得的金幣為基礎時間的兩倍
- **額外點擊按鈕**：每次升級增加 1 個點擊按鈕（最高 5 級）
- **自動點擊器**：自動點擊功能，頻率計算規則：
  - Lv.1：每 3 秒點擊 1 次
  - Lv.2：每 2 秒點擊 1 次
  - Lv.3：每 1 秒點擊 1 次
  - Lv.4+：每秒點擊 (等級-2) 次
  - 自動點擊器會作用於所有額外按鈕，總點擊頻率 = 單個點擊器頻率 × 額外按鈕數量

### PlayerPurchase（購買記錄）
- `user`: 玩家
- `shop_item`: 商店物品
- `level`: 當前等級
- `price_paid`: 支付價格

### Achievement（成就）
- `name`: 成就名稱
- `description`: 成就描述
- `achievement_type`: 成就類型
- `target_value`: 目標值
- `reward_coins`: 獎勵金幣
- `icon`: 圖標

### PlayerAchievement（玩家成就）
- `user`: 玩家
- `achievement`: 成就
- `unlocked_at`: 解鎖時間
- `reward_claimed`: 獎勵是否已領取（成就解鎖時自動領取獎勵）

**成就系統說明：**
- 成就分為三種類型：總點擊數（total_clicks）、單局點擊數（single_round）、總遊戲局數（total_games）
- 成就解鎖時會自動發放獎勵金幣，無需手動領取
- 玩家可以選擇最多 3 個已解鎖的成就作為徽章顯示在右上角

## API 端點

### 認證相關
- `POST /api/login/`: 登錄或註冊用戶（首次輸入用戶名會自動創建帳號）
- `POST /api/logout/`: 登出用戶

### 玩家資料
- `GET /api/profile/`: 獲取玩家資料、購買記錄、成就、徽章

### 遊戲相關
- `POST /api/submit-game/`: 提交遊戲結果（自動計算金幣、更新統計、檢查成就）
- `GET /api/history/`: 獲取遊戲歷史記錄（可選 limit 參數限制返回數量）

### 商店相關
- `GET /api/shop/`: 獲取商店物品列表（包含當前等級和下一級價格）
- `POST /api/purchase/`: 購買商店物品（價格計算：base_price × (current_level + 1)）

### 成就相關
- `GET /api/achievements/`: 獲取成就列表（包含解鎖狀態）
- `POST /api/update-badges/`: 更新用戶選擇的成就徽章（最多 3 個）

## 測試結構

測試用例位於 `game/Test_Cases/` 目錄：

- `test_case_01_game_flow.py`: 包含 12 個遊戲流程測試用例
  - 用戶登錄和註冊
  - 獲取用戶資料
  - 提交遊戲結果
  - 商店功能
  - 成就系統
  - 歷史記錄
  - 完整遊戲流程

## 部署配置

### Vercel
- `vercel.json`: Vercel 部署配置文件

### 環境變數
- `RENDER`: 用於判斷是否在 Render 平台
- `VERCEL`: 用於判斷是否在 Vercel 平台

## 開發工具

### 管理命令
- `python manage.py init_game_data`: 初始化遊戲資料（商店物品和成就）
- `python manage.py create_super_account`: 創建超級測試帳號（用於測試成就系統和商店物品功能）
  - 可選參數：`--username`（預設：super_test）、`--coins`（預設：1000000）

### 測試命令
- `python manage.py test game.Test_Cases.test_case_01_game_flow`: 運行遊戲流程測試

## 依賴套件

主要依賴（見 `requirements.txt`）：
- Django 5.1.7
- 其他必要的 Python 套件

## 注意事項

1. **虛擬環境**: `myenv/` 目錄不應提交到版本控制
2. **資料庫**: `db.sqlite3` 是開發環境的資料庫，生產環境應使用 PostgreSQL 等
3. **靜態文件**: 部署時需要配置靜態文件服務
4. **環境變數**: 生產環境應使用環境變數管理敏感資訊

