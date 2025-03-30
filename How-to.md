# Expected Structure

mygame_project/                 ← Django 專案資料夾
├── manage.py                  ← 管理指令工具
├── mygame_project/            ← 專案主設定資料夾
│   ├── __init__.py
│   ├── settings.py            ← 設定檔（DB, App, Templates 等）
│   ├── urls.py                ← 網址路由總入口
│   └── wsgi.py                ← 部署用
├── game/                      ← App：我們的遊戲核心
│   ├── migrations/            ← 資料庫版本紀錄
│   ├── templates/             ← HTML 模板
│   │   └── game/
│   │       └── home.html      ← 遊戲主畫面
│   ├── static/                ← 靜態資源（JS、CSS）
│   │   └── game/
│   │       └── script.js      ← 遊戲前端邏輯（可抽出來）
│   ├── views.py               ← 負責處理頁面邏輯
│   ├── models.py              ← 分數、使用者資料模型（可選）
│   ├── urls.py                ← 遊戲 app 的網址對應
│   └── admin.py / tests.py    ← 內建功能（可忽略）
└── requirements.txt           ← 套件清單（給部署用）


# schedule
//----------------------------------------------------------------
時間	    任務
1 小時	    安裝 Django、建立專案
2 小時	    前端寫遊戲邏輯（用 JS 實作反應遊戲）
1 小時	    Django 加入分數紀錄
1 小時	    美化畫面＋做首頁
1 小時	    加入使用者登入／簡單排行榜
1 小時	    部署到 render.com 或 vercel（免費）
剩下時間	測試＋優化或加動畫／音效

# VM Startup Script

env\Scripts\activate

pip install -r requirements.txt

python manage.py runserver

open http://127.0.0.1:8000