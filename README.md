# ClickFast 🖱️⚡

ClickFast 是一個快節奏的點擊遊戲！在時限內盡可能多地點擊，賺取金幣，購買升級，解鎖成就！

## 目錄

- [功能特色](#功能特色)
- [立即遊玩](#立即遊玩)
- [技術棧](#技術棧)
- [安裝說明](#安裝說明)
- [設置說明](#設置說明)
- [遊戲玩法](#遊戲玩法)
- [商店物品](#商店物品)
- [成就系統](#成就系統)
- [徽章系統](#徽章系統)
- [測試](#測試)
- [截圖](#截圖)
- [貢獻](#貢獻)
- [許可證](#許可證)

## 功能特色

- ⚡ **5秒點擊挑戰** - 在限定時間內盡可能多地點擊
- 💰 **貨幣系統** - 基礎時間（5秒）內每次點擊1金幣，延長時間內每次點擊2金幣
- 🛒 **商店系統** - 購買遊戲時間延長、額外點擊按鈕、自動點擊器
- 🎯 **多個點擊按鈕** - 購買額外按鈕增加點擊效率（最高5級）
- 🤖 **自動點擊器** - 自動幫你點擊，頻率隨等級提升（最高10級）
- 🏆 **成就系統** - 完成各種挑戰解鎖成就並自動獲得獎勵
- 🎖️ **徽章系統** - 選擇最多3個已解鎖的成就作為徽章顯示
- 💾 **雲端數據存儲** - 所有數據保存在雲端數據庫
- 📱 **響應式設計** - 支持桌面和移動設備

## 立即遊玩

- 👉 [ClickFast on Vercel](https://click-fast.vercel.app/)
- 👉 [ClickFast on Render](https://clickfast.onrender.com)

## 技術棧

- **後端**: Python (Django 5.1.7)
- **前端**: HTML5, CSS3, JavaScript (Vanilla)
- **數據庫**: SQLite3 (可配置為PostgreSQL等雲端數據庫)
- **部署**: Render, Vercel

## 安裝說明

```bash
# 克隆倉庫
git clone https://github.com/Kaimin018/ClickFast.git
cd ClickFast

# 創建虛擬環境（推薦）
python -m venv myenv
source myenv/bin/activate  # Windows: myenv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 執行數據庫遷移
python manage.py migrate

# 初始化遊戲數據（商店物品和成就）
python manage.py init_game_data

# 執行開發伺服器
python manage.py runserver
```

## 設置說明

### 1. 數據庫遷移

首次執行前需要創建數據庫表：

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. 初始化遊戲數據

執行管理命令初始化商店物品和成就：

```bash
python manage.py init_game_data
```

這將創建：
- 3種商店物品（遊戲時間延長、額外點擊按鈕、自動點擊器）
- 9個成就（總點擊、單局點擊、遊戲局數等）

### 3. 創建超級使用者（可選）

如果需要存取Django管理後台：

```bash
python manage.py createsuperuser
```

然後存取 `http://localhost:8000/admin/` 進行管理。

### 4. 創建超級測試帳號（可選）

用於測試成就系統和商店物品功能：

```bash
python manage.py create_super_account
```

或者指定使用者名稱和金幣數量：

```bash
python manage.py create_super_account --username test_user --coins 2000000
```

超級帳號將自動：
- 擁有大量金幣（預設 1,000,000）
- 購買所有商店物品到最高等級
- 解鎖所有成就（獎勵已自動領取）
- 擁有高額的遊戲統計數據（總點擊50000、單局最佳500、遊戲局數200、對戰勝場50）

### 5. 雲端數據庫配置（可選）

如果需要使用雲端數據庫（如PostgreSQL），修改 `react_game/settings.py`：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

## 遊戲玩法

1. **登入/註冊**: 輸入使用者名稱開始遊戲（首次輸入會自動創建帳號）
2. **點擊挑戰**: 點擊"開始遊戲"按鈕，在限定時間內盡可能多地點擊
3. **賺取金幣**: 
   - 基礎時間（5秒）內：每次點擊1金幣
   - 延長時間內：每次點擊2金幣
4. **購買升級**: 在商店購買升級來提升遊戲體驗
   - 延長遊戲時間以獲得更多金幣
   - 增加點擊按鈕數量以提高點擊效率
   - 啟用自動點擊器自動幫你點擊
5. **解鎖成就**: 完成各種挑戰自動解鎖成就並獲得獎勵金幣
6. **選擇徽章**: 選擇已解鎖的成就作為徽章顯示在右上角

## 商店物品

- **遊戲時間延長**: 每次升級增加2秒遊戲時間（最高10級）
  - 延長時間內點擊獲得的金幣為基礎時間的兩倍
  - 價格計算：基礎價格 × (當前等級 + 1)
  
- **額外點擊按鈕**: 每次升級增加1個點擊按鈕（最高5級）
  - 可以同時點擊多個按鈕增加點擊效率
  - 價格計算：基礎價格 × (當前等級 + 1)
  
- **自動點擊器**: 自動點擊功能，頻率隨等級提升（最高10級）
  - Lv.1：每 3 秒點擊 1 次
  - Lv.2：每 2 秒點擊 1 次
  - Lv.3：每 1 秒點擊 1 次
  - Lv.4+：每秒點擊 (等級-2) 次
  - 自動點擊器會作用於所有額外按鈕，總點擊頻率 = 單個點擊器頻率 × 額外按鈕數量
  - 價格計算：基礎價格 × (當前等級 + 1)

## 成就系統

成就分為三種類型，解鎖時會自動發放獎勵金幣：

- **總點擊成就**:
  - 🎯 初出茅廬：累計點擊100次（獎勵50金幣）
  - 🔥 點擊達人：累計點擊1000次（獎勵500金幣）
  - 👑 點擊大師：累計點擊10000次（獎勵5000金幣）

- **單局成就**:
  - ⚡ 單局突破：單局點擊超過50次（獎勵100金幣）
  - 💪 單局高手：單局點擊超過100次（獎勵500金幣）
  - 🌟 單局傳奇：單局點擊超過200次（獎勵2000金幣）

- **遊戲局數成就**:
  - 🎮 遊戲新手：完成10局遊戲（獎勵100金幣）
  - 🏅 遊戲老手：完成50局遊戲（獎勵500金幣）
  - 🏆 遊戲大師：完成100局遊戲（獎勵2000金幣）

## 徽章系統

- 玩家可以選擇最多3個已解鎖的成就作為徽章
- 徽章會顯示在遊戲界面右上角
- 可以隨時更換選擇的徽章

## 測試

專案包含完整的測試套件，按遊戲系統/模組分類：

### 運行測試

```bash
# 運行所有測試
python manage.py test game.Test_Cases --keepdb

# 運行特定模組測試
python manage.py test game.Test_Cases.01_Authentication_System --keepdb
python manage.py test game.Test_Cases.02_Core_Gameplay --keepdb
python manage.py test game.Test_Cases.07_Flow_And_E2E_Tests --keepdb
```

### 測試模組

- `01_Authentication_System` - 認證系統測試
- `02_Core_Gameplay` - 核心遊戲玩法測試
- `03_Shop_System` - 商店系統測試
- `04_Achievement_System` - 成就系統測試
- `05_UI_System` - UI 系統測試
- `06_Frontend_Responsive` - 前端響應式設計測試
- `07_Flow_And_E2E_Tests` - 流程與端到端測試
- `08_Technical_Checks` - 技術與非功能性測試（性能、驗證邏輯）

詳細測試說明請參考 `game/Test_Cases/TC_README.md`

## 截圖

![Gameplay Screenshot](./assets/screenshot.png)

## 貢獻

歡迎貢獻！請提交 issue 或 pull request。

## 許可證

本專案採用 MIT 許可證。