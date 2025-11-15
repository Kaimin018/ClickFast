# 用戶端資料儲存最佳實踐指南

本文檔說明 ClickFast 專案中用戶端資料儲存的最佳實踐和優化策略。

## 儲存策略總覽

根據資料類型和用途，我們採用不同的儲存方式：

| 資料類型 | 建議使用 | 原因 |
|---------|---------|------|
| **登入狀態 (Session)** | Cookie (Django Session) | 專為身分驗證設計，可設為 HTTP Only 增加安全性 |
| **遊戲設定、臨時進度** | LocalStorage | 簡單、容量夠用（5MB+）、存取速度快 |
| **複雜資料集** | IndexedDB | 支援結構化資料、更大的容量、進階查詢（未來擴展用） |

## 實作細節

### 1. 登入狀態管理（Cookie/Session）

#### 為什麼使用 Cookie 而不是 LocalStorage？

- **安全性**：HTTP Only Cookie 無法被 JavaScript 存取，防止 XSS 攻擊
- **自動管理**：Django Session 自動處理過期、續期等邏輯
- **伺服器端控制**：登出時伺服器可以立即清除 Session

#### 實作方式

```javascript
// ❌ 錯誤：使用 localStorage 儲存登入狀態
localStorage.setItem('clickfast_username', username);
localStorage.setItem('clickfast_logged_in', 'true');

// ✅ 正確：使用 Django Session Cookie（自動管理）
// 登入時，Django 會自動設置 Session Cookie
// 前端只需調用 API，不需要手動管理
await apiCall('/api/login/', 'POST', { username });
```

#### Django Session 配置

在 `react_game/settings.py` 中：

```python
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 天
SESSION_COOKIE_HTTPONLY = True  # 防止 XSS
SESSION_COOKIE_SECURE = False  # 本地開發設為 False，生產環境應設為 True（HTTPS）
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_SAVE_EVERY_REQUEST = True  # 每次請求都更新 session，延長過期時間
```

### 2. 遊戲設定管理（LocalStorage）

#### 使用場景

- 音量設定
- 音效開關
- 自動儲存設定
- 主題設定
- 其他用戶偏好

#### 實作方式

使用統一的 `StorageManager` 管理：

```javascript
// 讀取遊戲設定
const settings = StorageManager.getGameSettings();
// 返回：{ volume: 1.0, soundEnabled: true, autoSave: true, theme: 'default' }

// 儲存遊戲設定
StorageManager.saveGameSettings({
  volume: 0.8,
  soundEnabled: false,
  autoSave: true,
  theme: 'dark'
});
```

#### 預設值處理

```javascript
getDefaultSettings() {
  return {
    volume: 1.0,        // 音量 (0.0 - 1.0)
    soundEnabled: true, // 音效開關
    autoSave: true,     // 自動儲存
    theme: 'default',   // 主題
  };
}
```

### 3. 臨時遊戲進度（LocalStorage）

#### 使用場景

- 未完成的遊戲進度
- 臨時資料快取
- 離線遊戲狀態

#### 實作方式

```javascript
// 儲存遊戲進度
StorageManager.saveGameProgress({
  clicks: 150,
  timeRemaining: 3.5,
  timestamp: Date.now()
});

// 讀取遊戲進度
const progress = StorageManager.getGameProgress();

// 清除遊戲進度
StorageManager.clearGameProgress();
```

### 4. 最後用戶名（LocalStorage）

#### 使用場景

- 僅用於 UI 顯示和預填
- **不作為認證依據**
- 提升用戶體驗

#### 實作方式

```javascript
// 儲存最後使用的用戶名（僅用於 UI）
StorageManager.saveLastUsername('username');

// 讀取最後用戶名
const lastUsername = StorageManager.getLastUsername();

// 預填登入輸入框
if (lastUsername) {
  usernameInput.value = lastUsername;
}
```

## StorageManager API 參考

### 完整 API 列表

```javascript
const StorageManager = {
  // 遊戲設定
  getGameSettings()              // 讀取遊戲設定
  saveGameSettings(settings)      // 儲存遊戲設定
  getDefaultSettings()            // 取得預設設定
  
  // 遊戲進度
  getGameProgress()               // 讀取遊戲進度
  saveGameProgress(progress)      // 儲存遊戲進度
  clearGameProgress()             // 清除遊戲進度
  
  // 用戶名（僅用於 UI）
  getLastUsername()               // 讀取最後用戶名
  saveLastUsername(username)      // 儲存最後用戶名
  
  // 清除資料
  clearAllLocalData()             // 清除所有本地資料（登出時使用）
};
```

### 錯誤處理

所有 StorageManager 方法都包含錯誤處理：

```javascript
try {
  localStorage.setItem(key, value);
} catch (e) {
  console.error('儲存失敗:', e);
  // 優雅降級，不影響遊戲運行
}
```

## 安全性考量

### ✅ 最佳實踐

1. **登入狀態使用 Cookie**
   - HTTP Only Cookie 防止 XSS
   - SameSite 防止 CSRF
   - 伺服器端控制過期時間

2. **敏感資料不儲存在 LocalStorage**
   - 不儲存密碼、Token 等敏感資訊
   - 不將登入狀態儲存在 LocalStorage

3. **資料驗證**
   - 從 LocalStorage 讀取的資料需要驗證
   - 提供預設值作為降級方案

### ❌ 避免的做法

1. **不要在 LocalStorage 儲存登入狀態**
   ```javascript
   // ❌ 錯誤
   localStorage.setItem('is_logged_in', 'true');
   localStorage.setItem('auth_token', token);
   ```

2. **不要信任 LocalStorage 的資料**
   ```javascript
   // ❌ 錯誤：直接使用 LocalStorage 的資料作為認證
   if (localStorage.getItem('is_logged_in') === 'true') {
     // 允許存取
   }
   
   // ✅ 正確：總是向伺服器驗證
   const result = await apiCall('/api/profile/');
   if (result.profile) {
     // 有有效的 session
   }
   ```

## 性能優化

### 1. 非阻塞載入

```javascript
// ✅ 正確：非阻塞檢查 Session
async function checkSessionAsync() {
  try {
    const result = await fetch('/api/profile/', {
      method: 'GET',
      credentials: 'include',
    });
    if (result.ok) {
      applyLoginState();
    }
  } catch (e) {
    // 靜默處理，不影響頁面載入
  }
}
```

### 2. 緩存策略

- 遊戲設定：讀取頻繁，適合緩存在 LocalStorage
- 成就列表：使用記憶體緩存（`gameState.unlockedAchievements`）
- 用戶資料：由伺服器端 Session 管理

### 3. 資料清理

```javascript
// 登出時清除本地資料
StorageManager.clearAllLocalData();
// 保留遊戲設定和最後用戶名，方便下次使用
```

## 未來擴展

### IndexedDB 使用場景

當需要儲存大量結構化資料時，可以考慮使用 IndexedDB：

- 遊戲歷史記錄（離線查詢）
- 複雜的玩家庫存/裝備列表
- 需要進階查詢和篩選的資料

### 實作範例（未來）

```javascript
// IndexedDB 操作範例（未來擴展）
async function saveGameHistoryToIndexedDB(history) {
  const db = await openDB('clickfast_db', 1);
  await db.put('game_history', history);
}
```

## 測試建議

### 測試項目

1. **Session 管理測試**
   - 登入後 Session 是否正確設置
   - Session 過期後是否正確處理
   - 登出後 Session 是否清除

2. **LocalStorage 測試**
   - 設定儲存和讀取是否正常
   - 預設值是否正確應用
   - 錯誤處理是否優雅

3. **資料清理測試**
   - 登出時是否正確清除資料
   - 清除後是否保留必要資料（設定、用戶名）

## 相關文件

- `guidance/Structure.md` - 專案結構說明
- `guidance/How-to.md` - 開發和部署指南
- `game/templates/game/home.html` - 前端實作（包含 StorageManager）

## 更新記錄

- **2025-01-XX**: 初始版本
  - 建立 StorageManager 統一管理系統
  - 將登入狀態從 localStorage 改為 Cookie/Session
  - 優化資料儲存結構和安全性

