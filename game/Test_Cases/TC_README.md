# 測試用例說明

## 測試檔案結構（按遊戲系統/模組分類）

本專案採用**模式一：按「遊戲系統/模組」分類**作為主要架構，並結合**模式二：按「測試類型/目標」分類**作為補充。

```
Test_Cases/
├── 01_Authentication_System/          # 認證系統
│   ├── __init__.py
│   ├── TC_AUTH_001_Login_Register.py
│   ├── TC_AUTH_002_Session_Management.py
│   └── TC_AUTH_003_Validation_Unit.py
│
├── 02_Core_Gameplay/                  # 核心遊戲玩法
│   ├── __init__.py
│   ├── TC_GAME_001_Game_Flow.py
│   ├── TC_GAME_002_Coin_Calculation.py
│   └── TC_GAME_003_Record_Update.py
│
├── 03_Shop_System/                    # 商店系統
│   ├── __init__.py
│   ├── TC_SHOP_001_Item_List.py
│   └── TC_SHOP_002_Purchase_Function.py
│
├── 04_Achievement_System/             # 成就系統
│   ├── __init__.py
│   ├── TC_ACH_001_Achievement_List.py
│   └── TC_ACH_002_Achievement_Unlock.py
│
├── 05_UI_System/                      # UI系統
│   ├── __init__.py
│   ├── TC_UI_001_Page_Load.py
│   ├── TC_UI_002_Login_Flow.py
│   ├── TC_UI_003_Modal_Operations.py
│   └── TC_UI_004_Statistics_Display.py
│
├── 06_Frontend_Responsive/            # 前端響應式設計
│   ├── __init__.py
│   ├── TC_RESP_001_Mobile_Viewport.py
│   ├── TC_RESP_002_Mobile_Layout.py
│   └── TC_RESP_003_Touch_Optimization.py
│
├── 07_Flow_And_E2E_Tests/            # 流程與端到端測試
│   ├── __init__.py
│   └── TC_E2E_001_Complete_Game_Flow.py
│
└── 08_Technical_Checks/              # 技術與非功能性測試
    ├── __init__.py
    ├── TC_TECH_001_Performance.py
    └── TC_TECH_002_Validation_Edge_Cases.py
```

## 測試分類說明

### 01_Authentication_System（認證系統）
測試用戶登錄、註冊、Session 管理等功能。

### 02_Core_Gameplay（核心遊戲玩法）
測試遊戲核心機制：點擊、計時、金幣計算、記錄更新等。

### 03_Shop_System（商店系統）
測試商店物品列表、購買功能、價格計算等。

### 04_Achievement_System（成就系統）
測試成就列表、解鎖機制、獎勵發放等。

### 05_UI_System（UI系統）
測試前端頁面載入、登錄流程、模態框操作、統計資訊顯示等。

### 06_Frontend_Responsive（前端響應式設計）
測試手機版 viewport、響應式佈局、觸控優化等。

### 07_Flow_And_E2E_Tests（流程與端到端測試）
測試完整的遊戲流程，確保多個系統整合時不會出錯。

### 08_Technical_Checks（技術與非功能性測試）
測試性能、驗證邏輯、邊界情況等。

## 運行測試

### 運行特定系統的測試
```bash
# 認證系統測試
python manage.py test game.Test_Cases.01_Authentication_System

# 核心遊戲玩法測試
python manage.py test game.Test_Cases.02_Core_Gameplay

# 商店系統測試
python manage.py test game.Test_Cases.03_Shop_System

# 成就系統測試
python manage.py test game.Test_Cases.04_Achievement_System

# UI系統測試
python manage.py test game.Test_Cases.05_UI_System

# 前端響應式設計測試
python manage.py test game.Test_Cases.06_Frontend_Responsive

# 流程與端到端測試
python manage.py test game.Test_Cases.07_Flow_And_E2E_Tests

# 技術與非功能性測試
python manage.py test game.Test_Cases.08_Technical_Checks
```

### 運行所有測試
```bash
python manage.py test game.Test_Cases --keepdb
```

### 並行測試（僅適用於後端測試）
```bash
# 後端測試可以並行運行
python manage.py test game.Test_Cases.01_Authentication_System --parallel 4 --keepdb
python manage.py test game.Test_Cases.02_Core_Gameplay --parallel 4 --keepdb
python manage.py test game.Test_Cases.03_Shop_System --parallel 4 --keepdb
python manage.py test game.Test_Cases.04_Achievement_System --parallel 4 --keepdb
python manage.py test game.Test_Cases.07_Flow_And_E2E_Tests --parallel 4 --keepdb
python manage.py test game.Test_Cases.08_Technical_Checks --parallel 4 --keepdb

# 前端測試必須順序運行（因為需要啟動瀏覽器）
python manage.py test game.Test_Cases.05_UI_System --keepdb
python manage.py test game.Test_Cases.06_Frontend_Responsive --keepdb
```

## 測試用例命名規範

測試用例檔案命名遵循以下格式：
- `TC_[系統代碼]_[序號]_[功能描述].py`

系統代碼：
- `AUTH` - 認證系統 (Authentication)
- `GAME` - 核心遊戲玩法 (Core Gameplay)
- `SHOP` - 商店系統 (Shop)
- `ACH` - 成就系統 (Achievement)
- `UI` - UI系統 (UI System)
- `RESP` - 前端響應式設計 (Responsive)
- `E2E` - 流程與端到端測試 (End-to-End)
- `TECH` - 技術與非功能性測試 (Technical)

## 注意事項

1. **並行測試限制**：
   - 後端測試（01-04, 07-08）可以並行運行
   - 前端測試（05-06）必須順序運行，因為需要啟動瀏覽器

2. **資料庫**：
   - 使用 `--keepdb` 可以保留測試資料庫，下次測試更快

3. **前端測試**：
   - 需要 Chrome 瀏覽器和 ChromeDriver
   - 如果 Chrome 不可用，測試會自動跳過
