# 測試用例重構遷移指南

本文檔說明如何將現有的測試用例遷移到新的分類結構中。

## 新的資料夾結構

```
Test_Cases/
├── 01_Authentication_System/          # 認證系統
│   ├── TC_AUTH_001_Login_Register.py
│   ├── TC_AUTH_002_Session_Management.py
│   └── TC_AUTH_003_Validation_Unit.py
│
├── 02_Core_Gameplay/                  # 核心遊戲玩法
│   ├── TC_GAME_001_Game_Flow.py
│   ├── TC_GAME_002_Coin_Calculation.py
│   ├── TC_GAME_003_Record_Update.py
│   └── TC_GAME_004_Game_History.py
│
├── 03_Shop_System/                    # 商店系統
│   ├── TC_SHOP_001_Item_List.py
│   └── TC_SHOP_002_Purchase_Function.py
│
├── 04_Achievement_System/             # 成就系統
│   ├── TC_ACH_001_Achievement_List.py
│   └── TC_ACH_002_Achievement_Unlock.py
│
├── 05_UI_System/                      # UI系統
│   ├── TC_UI_001_Page_Load.py
│   ├── TC_UI_002_Login_Flow.py
│   ├── TC_UI_003_Modal_Operations.py
│   ├── TC_UI_004_Statistics_Display.py
│   └── TC_UI_005_Game_Operations.py
│
├── 06_Frontend_Responsive/            # 前端響應式設計
│   ├── TC_RESP_001_Mobile_Viewport.py
│   ├── TC_RESP_002_Mobile_Layout.py
│   └── TC_RESP_003_Touch_Optimization.py
│
├── 07_Flow_And_E2E_Tests/            # 流程與端到端測試
│   └── TC_E2E_001_Complete_Game_Flow.py
│
└── 08_Technical_Checks/              # 技術與非功能性測試
    ├── TC_TECH_001_Performance.py
    └── TC_TECH_002_Validation_Edge_Cases.py
```

## 測試用例映射表

### 從舊文件到新文件的映射

#### test_case_01_game_flow.py
- `test_case_01_user_login_and_register` → **01_Authentication_System/TC_AUTH_001_Login_Register.py** (部分)
- `test_case_02_get_user_profile` → **02_Core_Gameplay/TC_GAME_001_Game_Flow.py**
- `test_case_03_submit_game_result` → **02_Core_Gameplay/TC_GAME_001_Game_Flow.py**
- `test_case_04_submit_game_with_extended_time` → **02_Core_Gameplay/TC_GAME_002_Coin_Calculation.py**
- `test_case_05_get_shop_items` → **03_Shop_System/TC_SHOP_001_Item_List.py**
- `test_case_06_purchase_shop_item` → **03_Shop_System/TC_SHOP_002_Purchase_Function.py**
- `test_case_07_get_achievements` → **04_Achievement_System/TC_ACH_001_Achievement_List.py**
- `test_case_08_achievement_unlock` → **04_Achievement_System/TC_ACH_002_Achievement_Unlock.py**
- `test_case_09_get_game_history` → **02_Core_Gameplay/TC_GAME_004_Game_History.py**
- `test_case_10_complete_game_flow` → **07_Flow_And_E2E_Tests/TC_E2E_001_Complete_Game_Flow.py**
- `test_case_11_update_best_clicks_record` → **02_Core_Gameplay/TC_GAME_003_Record_Update.py**
- `test_case_12_purchase_multiple_levels` → **03_Shop_System/TC_SHOP_002_Purchase_Function.py**

#### test_case_02_frontend_mobile.py
- `test_case_01_mobile_viewport_settings` → **06_Frontend_Responsive/TC_RESP_001_Mobile_Viewport.py**
- `test_case_02_mobile_responsive_layout` → **06_Frontend_Responsive/TC_RESP_001_Mobile_Viewport.py**
- `test_case_03_mobile_login_interface` → **06_Frontend_Responsive/TC_RESP_001_Mobile_Viewport.py**
- `test_case_04_mobile_click_button_size` → **06_Frontend_Responsive/TC_RESP_002_Mobile_Layout.py**
- `test_case_05_mobile_touch_action_prevention` → **06_Frontend_Responsive/TC_RESP_003_Touch_Optimization.py**
- `test_case_06_mobile_rapid_clicking` → **06_Frontend_Responsive/TC_RESP_003_Touch_Optimization.py**
- `test_case_07_mobile_game_controls_layout` → **06_Frontend_Responsive/TC_RESP_002_Mobile_Layout.py**
- `test_case_08_mobile_statistics_display` → **06_Frontend_Responsive/TC_RESP_002_Mobile_Layout.py**
- `test_case_09_mobile_modal_responsive` → **06_Frontend_Responsive/TC_RESP_002_Mobile_Layout.py**
- `test_case_10_mobile_badge_display` → **06_Frontend_Responsive/TC_RESP_002_Mobile_Layout.py**

#### test_case_03_frontend_functionality.py
- `test_case_01_page_loads_successfully` → **05_UI_System/TC_UI_001_Page_Load.py**
- `test_case_02_user_login_flow` → **05_UI_System/TC_UI_002_Login_Flow.py**
- `test_case_03_game_start_and_click` → **05_UI_System/TC_UI_005_Game_Operations.py**
- `test_case_04_timer_countdown` → **08_Technical_Checks/TC_TECH_002_Validation_Edge_Cases.py** (單元測試)
- `test_case_05_shop_modal_open_close` → **05_UI_System/TC_UI_003_Modal_Operations.py**
- `test_case_06_achievements_modal_open_close` → **05_UI_System/TC_UI_003_Modal_Operations.py**
- `test_case_07_user_statistics_update` → **05_UI_System/TC_UI_004_Statistics_Display.py**
- `test_case_08_button_states` → **08_Technical_Checks/TC_TECH_002_Validation_Edge_Cases.py** (單元測試)
- `test_case_09_responsive_design_elements` → **05_UI_System/TC_UI_004_Statistics_Display.py**
- `test_case_10_css_classes_present` → **05_UI_System/TC_UI_004_Statistics_Display.py**

#### test_case_04_login_scenarios.py
- `test_case_01_new_user_registration` → **01_Authentication_System/TC_AUTH_001_Login_Register.py**
- `test_case_02_existing_user_login` → **01_Authentication_System/TC_AUTH_001_Login_Register.py**
- `test_case_03_empty_username` → **01_Authentication_System/TC_AUTH_003_Validation_Unit.py**
- `test_case_04_whitespace_only_username` → **01_Authentication_System/TC_AUTH_003_Validation_Unit.py**
- `test_case_05_username_with_leading_trailing_spaces` → **01_Authentication_System/TC_AUTH_003_Validation_Unit.py**
- `test_case_06_special_characters_username` → **01_Authentication_System/TC_AUTH_003_Validation_Unit.py**
- `test_case_07_long_username` → **01_Authentication_System/TC_AUTH_003_Validation_Unit.py**
- `test_case_08_session_persistence` → **01_Authentication_System/TC_AUTH_002_Session_Management.py**
- `test_case_09_logout_functionality` → **01_Authentication_System/TC_AUTH_002_Session_Management.py**
- `test_case_10_unauthorized_access` → **01_Authentication_System/TC_AUTH_002_Session_Management.py**
- `test_case_11_multiple_login_same_user` → **01_Authentication_System/TC_AUTH_001_Login_Register.py**
- `test_case_12_different_users_login` → **01_Authentication_System/TC_AUTH_001_Login_Register.py**
- `test_case_13_login_with_profile_data` → **01_Authentication_System/TC_AUTH_001_Login_Register.py**
- `test_case_14_login_after_logout` → **01_Authentication_System/TC_AUTH_002_Session_Management.py**
- `test_case_15_case_sensitive_username` → **01_Authentication_System/TC_AUTH_003_Validation_Unit.py**
- `test_case_16_missing_username_field` → **01_Authentication_System/TC_AUTH_003_Validation_Unit.py**
- `test_case_17_invalid_json` → **01_Authentication_System/TC_AUTH_003_Validation_Unit.py**
- `test_case_18_get_method_not_allowed` → **01_Authentication_System/TC_AUTH_003_Validation_Unit.py**
- `test_case_19_concurrent_login_different_clients` → **01_Authentication_System/TC_AUTH_001_Login_Register.py**

## 已完成的工作

✅ 已創建所有新的資料夾結構
✅ 已創建所有系統的 `__init__.py` 文件
✅ 已創建主要測試文件：
- 01_Authentication_System (3個文件)
- 02_Core_Gameplay (4個文件)
- 03_Shop_System (2個文件)
- 04_Achievement_System (2個文件)
- 05_UI_System (5個文件)
- 06_Frontend_Responsive (3個文件)
- 07_Flow_And_E2E_Tests (1個文件)
- 08_Technical_Checks (2個文件)

## 已完成的工作

✅ 已創建所有新的資料夾結構
✅ 已創建所有系統的 `__init__.py` 文件
✅ 已創建主要測試文件：
- 01_Authentication_System (3個文件)
- 02_Core_Gameplay (4個文件)
- 03_Shop_System (2個文件)
- 04_Achievement_System (2個文件)
- 05_UI_System (5個文件)
- 06_Frontend_Responsive (3個文件)
- 07_Flow_And_E2E_Tests (1個文件)
- 08_Technical_Checks (2個文件)
✅ **已刪除舊測試文件**（已完全遷移到新結構）
✅ **已更新 CI/CD 配置**（`.github/workflows/test.yml`）

## 驗證新測試結構

運行以下命令驗證新測試結構是否正常工作：

```bash
# 測試認證系統
python manage.py test game.Test_Cases.01_Authentication_System --keepdb

# 測試核心遊戲玩法
python manage.py test game.Test_Cases.02_Core_Gameplay --keepdb

# 測試商店系統
python manage.py test game.Test_Cases.03_Shop_System --keepdb

# 測試成就系統
python manage.py test game.Test_Cases.04_Achievement_System --keepdb

# 測試 UI 系統
python manage.py test game.Test_Cases.05_UI_System --keepdb

# 測試前端響應式設計
python manage.py test game.Test_Cases.06_Frontend_Responsive --keepdb

# 測試流程與端到端測試
python manage.py test game.Test_Cases.07_Flow_And_E2E_Tests --keepdb

# 測試技術與非功能性測試
python manage.py test game.Test_Cases.08_Technical_Checks --keepdb
```

## CI/CD 配置

CI/CD 配置已更新為使用新的測試結構：

### 後端測試（django-tests job）
- `01_Authentication_System`
- `02_Core_Gameplay`
- `03_Shop_System`
- `04_Achievement_System`
- `07_Flow_And_E2E_Tests`
- `08_Technical_Checks`

### 前端測試（frontend-tests job）
- `05_UI_System`
- `06_Frontend_Responsive`

詳細配置請參考 `.github/workflows/test.yml`

