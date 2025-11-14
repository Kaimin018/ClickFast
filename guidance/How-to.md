# ClickFast 開發和部署指南

## 開發時間表

| 時間 | 任務 |
|------|------|
| 1 小時 | 安裝 Django、建立專案 |
| 2 小時 | 前端寫遊戲邏輯（用 JS 實作反應遊戲） |
| 1 小時 | Django 加入分數紀錄 |
| 1 小時 | 美化畫面＋做首頁 |
| 1 小時 | 加入使用者登入／簡單排行榜 |
| 1 小時 | 部署到 render.com 或 vercel（免費） |
| 剩下時間 | 測試＋優化或加動畫／音效 |

## 建立依賴檔案

```bash
pip freeze > requirements.txt
```

## 虛擬環境啟動腳本

```powershell
# 建立虛擬環境
python -m venv myenv

# 啟動虛擬環境
myenv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 執行資料庫遷移
python manage.py migrate

# 初始化遊戲資料
python manage.py init_game_data

# 啟動開發伺服器
python manage.py runserver

# 開啟瀏覽器
# http://127.0.0.1:8000
```

## Vercel 部署設定

參考教學影片：[Deploy a Django web app to Vercel](https://www.youtube.com/watch?v=ZjVzHcXCeMU)

## 部署平台

- **Render**: 免費方案可用，支援 PostgreSQL
- **Vercel**: 免費方案可用，適合靜態和 Serverless 函數
- **Railway**: 付費平台
- **Fly.io**: 付費平台

詳細部署說明請參考 `local-testing-guide.md` 和 `Structure.md`。