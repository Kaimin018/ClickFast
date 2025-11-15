"""
遊戲測試用例模組（按遊戲系統/模組分類）

推薦的測試運行方式：

1. 後端測試（推薦不使用並行，避免 PostgreSQL 連接問題）：
   python manage.py test game.Test_Cases.01_Authentication_System --keepdb
   python manage.py test game.Test_Cases.02_Core_Gameplay --keepdb
   python manage.py test game.Test_Cases.03_Shop_System --keepdb
   python manage.py test game.Test_Cases.04_Achievement_System --keepdb
   python manage.py test game.Test_Cases.07_Flow_And_E2E_Tests --keepdb
   python manage.py test game.Test_Cases.08_Technical_Checks --keepdb

   或者一次性運行所有後端測試：
   python manage.py test game.Test_Cases.01_Authentication_System game.Test_Cases.02_Core_Gameplay game.Test_Cases.03_Shop_System game.Test_Cases.04_Achievement_System game.Test_Cases.07_Flow_And_E2E_Tests game.Test_Cases.08_Technical_Checks --keepdb

   注意：如果使用 PostgreSQL，不建議使用 --parallel 選項，因為會遇到資料庫連接問題。
   如果使用 SQLite，可以使用 --parallel 4 來加速測試。

2. 前端測試（順序運行，因為需要瀏覽器）：
   python manage.py test game.Test_Cases.05_UI_System --keepdb
   python manage.py test game.Test_Cases.06_Frontend_Responsive --keepdb

3. 流程與端到端測試：
   python manage.py test game.Test_Cases.07_Flow_And_E2E_Tests --keepdb

4. 所有測試（順序運行）：
   python manage.py test game.Test_Cases --keepdb

注意事項：
- 前端測試不適合並行運行，因為需要啟動瀏覽器實例
- 使用 PostgreSQL 時，並行測試可能會遇到 "database is being accessed by other users" 錯誤
- 使用 --keepdb 可以保留測試資料庫，加快後續測試速度
- 前端測試需要 Chrome 瀏覽器和 ChromeDriver，如果不可用會自動跳過
"""
