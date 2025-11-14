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

# create requirement
pip freeze > requirement.txt

# VM Startup Script

python -m venv myenv
myenv\Scripts\activate

pip install -r requirements.txt

python manage.py runserver

open http://127.0.0.1:8000

# Vercel seetting 

[Deploy a Django web app to Vercel](https://www.youtube.com/watch?v=ZjVzHcXCeMU)