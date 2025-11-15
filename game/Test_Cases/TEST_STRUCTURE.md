# 測試用例結構說明

## 分類架構

本專案採用**模式一：按「遊戲系統/模組」分類**作為主要架構，並結合**模式二：按「測試類型/目標」分類**作為補充。

## 資料夾結構

```
Test_Cases/
├── 01_Authentication_System/          # 認證系統
│   ├── __init__.py
│   ├── TC_AUTH_001_Login_Register.py          # 登錄與註冊功能
│   ├── TC_AUTH_002_Session_Management.py     # Session 管理
│   └── TC_AUTH_003_Validation_Unit.py         # 驗證邏輯單元測試
│
├── 02_Core_Gameplay/                  # 核心遊戲玩法
│   ├── __init__.py
│   ├── TC_GAME_001_Game_Flow.py              # 遊戲基本流程和結果提交
│   ├── TC_GAME_002_Coin_Calculation.py       # 金幣計算邏輯
│   ├── TC_GAME_003_Record_Update.py          # 最佳點擊記錄更新
│   └── TC_GAME_004_Game_History.py           # 遊戲歷史記錄查詢
│
├── 03_Shop_System/                    # 商店系統
│   ├── __init__.py
│   ├── TC_SHOP_001_Item_List.py              # 商店物品列表查詢
│   └── TC_SHOP_002_Purchase_Function.py      # 購買功能和價格計算
│
├── 04_Achievement_System/             # 成就系統
│   ├── __init__.py
│   ├── TC_ACH_001_Achievement_List.py        # 成就列表查詢
│   └── TC_ACH_002_Achievement_Unlock.py      # 成就解鎖機制和獎勵發放
│
├── 05_UI_System/                      # UI系統
│   ├── __init__.py
│   ├── TC_UI_001_Page_Load.py                # 頁面成功載入
│   ├── TC_UI_002_Login_Flow.py               # 用戶登錄流程
│   ├── TC_UI_003_Modal_Operations.py         # 商店和成就模態框操作
│   ├── TC_UI_004_Statistics_Display.py       # 統計資訊顯示和響應式設計
│   └── TC_UI_005_Game_Operations.py          # 遊戲開始和點擊功能
│
├── 06_Frontend_Responsive/            # 前端響應式設計
│   ├── __init__.py
│   ├── TC_RESP_001_Mobile_Viewport.py        # 手機版 viewport 設置和響應式佈局
│   ├── TC_RESP_002_Mobile_Layout.py          # 手機版按鈕大小、控制佈局、統計資訊
│   └── TC_RESP_003_Touch_Optimization.py     # 觸控動作防縮放和快速連點
│
├── 07_Flow_And_E2E_Tests/            # 流程與端到端測試
│   ├── __init__.py
│   └── TC_E2E_001_Complete_Game_Flow.py     # 完整遊戲流程端到端測試
│
└── 08_Technical_Checks/              # 技術與非功能性測試
    ├── __init__.py
    ├── TC_TECH_001_Performance.py            # API 響應時間和資料庫查詢效能
    └── TC_TECH_002_Validation_Edge_Cases.py  # 參數驗證和邊界情況
```

## 系統說明

### 01_Authentication_System（認證系統）
**測試範圍**：用戶登錄、註冊、Session 管理、驗證邏輯

**測試文件**：
- `TC_AUTH_001_Login_Register.py` - 登錄與註冊功能（6個測試用例）
- `TC_AUTH_002_Session_Management.py` - Session 持久性和登出功能（4個測試用例）
- `TC_AUTH_003_Validation_Unit.py` - 用戶名驗證邏輯（9個測試用例）

**總計**：19個測試用例

### 02_Core_Gameplay（核心遊戲玩法）
**測試範圍**：遊戲核心機制、點擊、計時、金幣計算、記錄更新

**測試文件**：
- `TC_GAME_001_Game_Flow.py` - 遊戲基本流程和結果提交（2個測試用例）
- `TC_GAME_002_Coin_Calculation.py` - 金幣計算邏輯（1個測試用例）
- `TC_GAME_003_Record_Update.py` - 最佳點擊記錄更新（1個測試用例）
- `TC_GAME_004_Game_History.py` - 遊戲歷史記錄查詢（1個測試用例）

**總計**：5個測試用例

### 03_Shop_System（商店系統）
**測試範圍**：商店物品列表、購買功能、價格計算

**測試文件**：
- `TC_SHOP_001_Item_List.py` - 商店物品列表查詢（1個測試用例）
- `TC_SHOP_002_Purchase_Function.py` - 購買功能和價格計算（2個測試用例）

**總計**：3個測試用例

### 04_Achievement_System（成就系統）
**測試範圍**：成就列表、解鎖機制、獎勵發放

**測試文件**：
- `TC_ACH_001_Achievement_List.py` - 成就列表查詢（1個測試用例）
- `TC_ACH_002_Achievement_Unlock.py` - 成就解鎖機制和獎勵發放（1個測試用例）

**總計**：2個測試用例

### 05_UI_System（UI系統）
**測試範圍**：前端頁面載入、登錄流程、模態框操作、統計資訊顯示

**測試文件**：
- `TC_UI_001_Page_Load.py` - 頁面成功載入（1個測試用例）
- `TC_UI_002_Login_Flow.py` - 用戶登錄流程（1個測試用例）
- `TC_UI_003_Modal_Operations.py` - 商店和成就模態框操作（2個測試用例）
- `TC_UI_004_Statistics_Display.py` - 統計資訊顯示和響應式設計（3個測試用例）
- `TC_UI_005_Game_Operations.py` - 遊戲開始和點擊功能（1個測試用例）

**總計**：8個測試用例

### 06_Frontend_Responsive（前端響應式設計）
**測試範圍**：手機版 viewport、響應式佈局、觸控優化

**測試文件**：
- `TC_RESP_001_Mobile_Viewport.py` - 手機版 viewport 設置和響應式佈局（3個測試用例）
- `TC_RESP_002_Mobile_Layout.py` - 手機版按鈕大小、控制佈局、統計資訊（4個測試用例）
- `TC_RESP_003_Touch_Optimization.py` - 觸控動作防縮放和快速連點（2個測試用例）

**總計**：9個測試用例

### 07_Flow_And_E2E_Tests（流程與端到端測試）
**測試範圍**：完整的遊戲流程，確保多個系統整合時不會出錯

**測試文件**：
- `TC_E2E_001_Complete_Game_Flow.py` - 完整遊戲流程端到端測試（1個測試用例）

**總計**：1個測試用例

### 08_Technical_Checks（技術與非功能性測試）
**測試範圍**：性能、驗證邏輯、邊界情況

**測試文件**：
- `TC_TECH_001_Performance.py` - API 響應時間測試（3個測試用例）
- `TC_TECH_002_Validation_Edge_Cases.py` - 參數驗證和邊界情況（4個測試用例）

**總計**：7個測試用例

## 測試統計

### 總測試用例數：54 個

- **01_Authentication_System**：19 個
- **02_Core_Gameplay**：5 個
- **03_Shop_System**：3 個
- **04_Achievement_System**：2 個
- **05_UI_System**：8 個
- **06_Frontend_Responsive**：9 個
- **07_Flow_And_E2E_Tests**：1 個
- **08_Technical_Checks**：7 個

## 測試命名規範

測試用例檔案命名遵循以下格式：
- `TC_[系統代碼]_[序號]_[功能描述].py`

**系統代碼**：
- `AUTH` - 認證系統 (Authentication)
- `GAME` - 核心遊戲玩法 (Core Gameplay)
- `SHOP` - 商店系統 (Shop)
- `ACH` - 成就系統 (Achievement)
- `UI` - UI系統 (UI System)
- `RESP` - 前端響應式設計 (Responsive)
- `E2E` - 流程與端到端測試 (End-to-End)
- `TECH` - 技術與非功能性測試 (Technical)

## 優點

✅ **高效率**：測試人員可以快速找到與特定 Bug 相關的測試案例

✅ **清晰分工**：易於將不同系統的測試任務分配給專門的 QA 人員

✅ **易於維護**：當某個系統（如商店系統）進行大改版時，只需更新其對應資料夾內的案例

✅ **專注目標**：方便測試人員集中執行特定目標的測試（例如，在發布前只執行「流程與端到端測試」）

✅ **跨系統整合**：「Flow/E2E」資料夾專門用於確保多個系統整合時不會出錯

