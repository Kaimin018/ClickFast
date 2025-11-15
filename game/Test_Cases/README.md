# 測試用例說明

## 測試檔案結構

- `test_case_01_game_flow.py` - 後端遊戲流程測試（12 個測試用例）
- `test_case_02_frontend_mobile.py` - 前端手機版測試（10 個測試用例）
- `test_case_03_frontend_functionality.py` - 前端功能測試（10 個測試用例）

## 運行測試

### 基本命令

```bash
# 運行所有測試
python manage.py test game.Test_Cases

# 運行特定測試檔案
python manage.py test game.Test_Cases.test_case_01_game_flow
python manage.py test game.Test_Cases.test_case_02_frontend_mobile
python manage.py test game.Test_Cases.test_case_03_frontend_functionality
```

### 並行測試（加速）

**重要**：只有後端測試適合並行運行，前端測試（Selenium）必須順序運行！

```bash
# 後端測試：使用並行（推薦）
python manage.py test game.Test_Cases.test_case_01_game_flow --parallel 4 --keepdb

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
```

