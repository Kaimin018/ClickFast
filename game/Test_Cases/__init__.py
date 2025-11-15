"""
遊戲測試用例模組

推薦的測試運行方式：

1. 後端測試（並行，快速）：
    python manage.py test game.Test_Cases.test_case_01_game_flow --parallel 4 --keepdb

2. 前端測試（順序運行，因為需要瀏覽器）：
    python manage.py test game.Test_Cases.test_case_02_frontend_mobile --keepdb
    python manage.py test game.Test_Cases.test_case_03_frontend_functionality --keepdb

3. 所有測試（順序運行）：
    python manage.py test game.Test_Cases --keepdb

注意：前端測試不適合並行運行，因為需要啟動瀏覽器實例。
"""

