# ClickFast 部署平台備註

## 支援的部署平台

### 免費平台
- **Render**: 
  - 免費方案可用
  - 支援 PostgreSQL 資料庫
  - 部署網址：https://clickfast.onrender.com
  
- **Vercel**: 
  - 免費方案可用
  - 適合靜態和 Serverless 函數
  - 部署網址：https://click-fast.vercel.app/
  - 教學影片：[Deploy a Django web app to Vercel](https://www.youtube.com/watch?v=ZjVzHcXCeMU)

### 付費平台
- **Railway**: 付費平台，提供更多資源和功能
- **Fly.io**: 付費平台，全球分散式部署

## 環境變數設定

在 `react_game/settings.py` 中，系統會根據環境變數自動判斷部署平台：

- `RENDER`: 設定後會允許 `clickfast.onrender.com` 主機
- `VERCEL`: 設定後會允許 `.vercel.app` 主機

## 資料庫配置

- **開發環境**: 使用 SQLite3（`db.sqlite3`）
- **生產環境**: 建議使用 PostgreSQL 等雲端資料庫

詳細配置請參考 `README.md` 中的「雲端資料庫配置」章節。
