# 測試用例說明

## 測試檔案結構

- `test_case_01_game_flow.py` - 後端遊戲流程測試（12 個測試用例）
- `test_case_02_frontend_mobile.py` - 前端手機版測試（10 個測試用例）
- `test_case_03_frontend_functionality.py` - 前端功能測試（10 個測試用例）
- `test_case_04_login_scenarios.py` - 登入狀況測試（19 個測試用例）

## 運行測試

### 基本命令

```bash
# 運行所有測試
python manage.py test game.Test_Cases

# 運行特定測試檔案
python manage.py test game.Test_Cases.test_case_01_game_flow
python manage.py test game.Test_Cases.test_case_02_frontend_mobile
python manage.py test game.Test_Cases.test_case_03_frontend_functionality
python manage.py test game.Test_Cases.test_case_04_login_scenarios
```

### 並行測試（加速）

**重要**：只有後端測試適合並行運行，前端測試（Selenium）必須順序運行！

```bash
# 後端測試：使用並行（推薦）
python manage.py test game.Test_Cases.test_case_01_game_flow --parallel 4 --keepdb
python manage.py test game.Test_Cases.test_case_04_login_scenarios --parallel 4 --keepdb

# 前端測試：必須順序運行（因為需要啟動瀏覽器）
python manage.py test game.Test_Cases.test_case_02_frontend_mobile --keepdb
python manage.py test game.Test_Cases.test_case_03_frontend_functionality --keepdb

# ⚠️ 不建議：所有測試一起並行（前端測試會失敗）
# python manage.py test game.Test_Cases --parallel  # 不推薦
```

### 其他有用的選項

```bash
# 詳細輸出
python manage.py test game.Test_Cases --verbosity=2

# 保留測試資料庫（避免重複創建）
python manage.py test game.Test_Cases --keepdb

# 並行 + 保留資料庫 + 詳細輸出
python manage.py test game.Test_Cases --parallel 4 --keepdb --verbosity=2

# 只運行失敗的測試
python manage.py test game.Test_Cases --failfast
```

## 注意事項

1. **並行測試限制**：
   - 後端測試（`test_case_01_game_flow.py`）可以很好地並行運行
   - 前端測試（Selenium）並行時需要更多資源，建議單獨運行或使用較少的並行數

2. **資料庫**：
   - 並行測試會自動創建多個測試資料庫（`test_postgres_1`, `test_postgres_2` 等）
   - 使用 `--keepdb` 可以保留這些資料庫，下次測試更快

3. **前端測試**：
   - 需要 Chrome 瀏覽器和 ChromeDriver
   - 如果 Chrome 不可用，測試會自動跳過
   - 建議在 CI/CD 環境中運行前端測試

## 推薦的測試命令

### 快速測試（只運行後端測試，最快）
```bash
# 使用 SQLite（避免 PostgreSQL 連接問題）
$env:USE_SQLITE="true"; python manage.py test game.Test_Cases.test_case_01_game_flow --parallel 4 --keepdb

# 或使用 PostgreSQL
python manage.py test game.Test_Cases.test_case_01_game_flow --parallel 4 --keepdb
```

### 完整測試（所有測試）
```bash
# 設置使用 SQLite（推薦本地測試）
$env:USE_SQLITE="true"

# 後端測試（並行，快速）
python manage.py test game.Test_Cases.test_case_01_game_flow --parallel 4 --keepdb
python manage.py test game.Test_Cases.test_case_04_login_scenarios --parallel 4 --keepdb

# 前端測試（順序運行，因為需要瀏覽器）
python manage.py test game.Test_Cases.test_case_02_frontend_mobile --keepdb
python manage.py test game.Test_Cases.test_case_03_frontend_functionality --keepdb
```

### 所有測試（順序運行，較慢但穩定）
```bash
# 使用 SQLite
$env:USE_SQLITE="true"; python manage.py test game.Test_Cases --keepdb
```

### 開發時快速測試
```bash
# 只運行特定測試用例
python manage.py test game.Test_Cases.test_case_01_game_flow.GameFlowTestCase.test_case_01_user_login_and_register --keepdb
python manage.py test game.Test_Cases.test_case_04_login_scenarios.LoginScenariosTestCase.test_case_01_new_user_registration --keepdb
```

## 測試用例詳細說明

### test_case_04_login_scenarios.py - 登入狀況測試

此測試文件包含 19 個測試用例，涵蓋各種登入場景：

1. **test_case_01_new_user_registration** - 新用戶註冊
2. **test_case_02_existing_user_login** - 已存在用戶登入
3. **test_case_03_empty_username** - 空用戶名
4. **test_case_04_whitespace_only_username** - 只有空白字符的用戶名
5. **test_case_05_username_with_leading_trailing_spaces** - 用戶名前後有空格（trim 處理）
6. **test_case_06_special_characters_username** - 特殊字符用戶名
7. **test_case_07_long_username** - 長用戶名
8. **test_case_08_session_persistence** - Session 持久性
9. **test_case_09_logout_functionality** - 登出功能
10. **test_case_10_unauthorized_access** - 未登入狀態訪問受保護的 API
11. **test_case_11_multiple_login_same_user** - 同一用戶多次登入
12. **test_case_12_different_users_login** - 不同用戶登入
13. **test_case_13_login_with_profile_data** - 登入後驗證玩家資料完整性
14. **test_case_14_login_after_logout** - 登出後重新登入
15. **test_case_15_case_sensitive_username** - 用戶名大小寫敏感性
16. **test_case_16_missing_username_field** - 缺少用戶名字段
17. **test_case_17_invalid_json** - 無效的 JSON 格式
18. **test_case_18_get_method_not_allowed** - GET 方法不被允許
19. **test_case_19_concurrent_login_different_clients** - 不同客戶端同時登入同一用戶

