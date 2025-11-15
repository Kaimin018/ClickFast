# Git Revert 操作指南

本文檔說明如何在 ClickFast 專案中使用 Git revert 來安全地撤銷 commit，並提供實際範例。

## 什麼是 Git Revert？

`git revert` 是一個安全的撤銷操作，它會建立一個新的 commit 來撤銷指定 commit 的變更，而不會修改歷史記錄。這與 `git reset` 不同，`git reset` 會直接修改歷史記錄。

### Revert vs Reset 的差異

| 操作 | 用途 | 是否修改歷史 | 適用場景 |
|------|------|------------|---------|
| **git revert** | 建立新 commit 撤銷變更 | ❌ 不修改 | 已推送到遠端的 commit |
| **git reset** | 直接刪除 commit | ✅ 修改 | 僅限本地未推送的 commit |

## 基本操作步驟

### 1. 查看 Commit 歷史

在執行 revert 之前，先查看 commit 歷史以確定要 revert 的目標：

```powershell
# 查看簡短的 commit 歷史（推薦）
git log --oneline -10

# 查看詳細的 commit 歷史
git log -10

# 查看圖形化的分支歷史
git log --oneline --graph -10
```

### 2. 檢查當前狀態

確保工作目錄是乾淨的：

```powershell
git status
```

如果有未提交的變更，請先提交或暫存：

```powershell
# 暫存變更
git stash

# 或提交變更
git add .
git commit -m "你的 commit 訊息"
```

### 3. Revert 單個 Commit

#### Revert 最新的 Commit（HEAD）

```powershell
# 使用預設的 commit 訊息
git revert HEAD --no-edit

# 或自訂 commit 訊息
git revert HEAD -m "Revert: 撤銷最新的變更"
```

#### Revert 指定的 Commit

```powershell
# 使用 commit hash
git revert <commit-hash> --no-edit

# 範例：revert commit e0e3be3
git revert e0e3be3 --no-edit
```

### 4. Revert 多個 Commit

```powershell
# Revert 多個連續的 commit（從舊到新）
git revert <oldest-commit>..<newest-commit>

# 範例：revert 從 commit A 到 commit B 之間的所有變更
git revert 63ac598..e0e3be3 --no-edit
```

## 實際範例：Revert 到 3 個版本之前

以下範例展示如何 revert 到 3 個版本之前的狀態。

### 步驟 1：查看當前 Commit 歷史

```powershell
git log --oneline -10
```

假設輸出如下：

```
ab6727a Revert "Refactor home.html..."
e0e3be3 Refactor home.html to improve mobile responsiveness...
80c3b9d Implement StorageManager for client-side data management...
63ac598 Enhance item purchase validation in views.py...
1a4b383 Update README.md to include new sections...
```

### 步驟 2：確定目標 Commit

假設我們要 revert 到 3 個版本之前（即 `63ac598`），這意味著我們需要 revert 以下 commit：
- `ab6727a` (HEAD)
- `e0e3be3` (HEAD~1)
- `80c3b9d` (HEAD~2)

### 步驟 3：執行 Revert

有兩種方式可以達到目標：

#### 方法 A：逐個 Revert（推薦）

從最新的 commit 開始，依序 revert：

```powershell
# Revert 最新的 commit (ab6727a)
git revert ab6727a --no-edit

# Revert 第二個 commit (e0e3be3)
git revert e0e3be3 --no-edit

# Revert 第三個 commit (80c3b9d)
git revert 80c3b9d --no-edit
```

#### 方法 B：使用範圍 Revert

```powershell
# Revert 從 HEAD~2 到 HEAD 的所有 commit（不包含 HEAD~2）
git revert --no-commit HEAD~2..HEAD
git commit -m "Revert commits to restore state 3 versions ago"
```

**注意**：範圍 revert 的語法 `A..B` 表示從 A（不包含）到 B（包含）的所有 commit。

### 步驟 4：驗證結果

```powershell
# 查看新的 commit 歷史
git log --oneline -10

# 檢查檔案狀態
git status

# 查看變更內容
git diff HEAD~3
```

### 步驟 5：推送到遠端（如果需要）

```powershell
# 推送到遠端 repository
git push origin main

# 如果遠端有衝突，可能需要強制推送（謹慎使用）
# git push origin main --force
```

## 使用相對引用

Git 提供方便的相對引用語法：

| 語法 | 說明 | 範例 |
|------|------|------|
| `HEAD` | 當前 commit | `git revert HEAD` |
| `HEAD~1` | 上一個 commit | `git revert HEAD~1` |
| `HEAD~2` | 上上個 commit | `git revert HEAD~2` |
| `HEAD~3` | 3 個版本之前 | `git revert HEAD~3` |
| `HEAD~n` | n 個版本之前 | `git revert HEAD~n` |

### 範例：Revert 到 3 個版本之前（使用相對引用）

```powershell
# 查看 3 個版本之前的 commit
git show HEAD~3

# Revert 3 個版本之前的 commit
git revert HEAD~3 --no-edit

# 如果要 revert 從 HEAD~3 到 HEAD 的所有變更
git revert --no-commit HEAD~3..HEAD
git commit -m "Revert to state 3 versions ago"
```

## 處理衝突

如果 revert 過程中發生衝突：

### 1. 查看衝突檔案

```powershell
git status
```

### 2. 手動解決衝突

開啟衝突檔案，找到衝突標記：

```
<<<<<<< HEAD
當前的程式碼
=======
要 revert 的程式碼
>>>>>>> parent of <commit-hash>
```

手動編輯檔案，移除衝突標記並保留正確的程式碼。

### 3. 標記衝突已解決

```powershell
# 將解決後的檔案加入暫存區
git add <衝突檔案>

# 繼續 revert 流程
git revert --continue
```

### 4. 取消 Revert（如果需要）

```powershell
# 取消當前的 revert 操作
git revert --abort
```

## 最佳實踐

### ✅ 建議做法

1. **先查看歷史**：執行 revert 前務必先查看 commit 歷史
2. **確保工作目錄乾淨**：revert 前先提交或暫存未完成的變更
3. **使用 --no-edit**：如果預設的 revert commit 訊息可以接受
4. **測試變更**：revert 後測試應用程式確保功能正常
5. **保留歷史記錄**：使用 `git revert` 而非 `git reset` 來保留完整的歷史

### ❌ 避免的做法

1. **不要 revert 已推送的 commit 使用 reset**：這會破壞團隊協作
2. **不要忽略衝突**：必須手動解決所有衝突
3. **不要在未測試的情況下推送**：revert 後應先測試再推送
4. **不要 revert merge commit 時忘記指定 parent**：merge commit 有多個 parent，需要指定 `-m` 參數

## 特殊情況處理

### Revert Merge Commit

如果 commit 是一個 merge commit，需要指定要 revert 到哪個 parent：

```powershell
# 查看 merge commit 的 parents
git show <merge-commit-hash>

# Revert merge commit，指定 parent（通常是 1）
git revert -m 1 <merge-commit-hash> --no-edit
```

### 查看 Revert 的影響範圍

```powershell
# 查看哪些檔案會被影響
git show <commit-hash> --stat

# 查看詳細的變更內容
git show <commit-hash>
```

## 常見問題

### Q: Revert 後如何再次套用被 revert 的變更？

A: 可以再次 revert revert commit，或使用 `git cherry-pick` 重新套用原始 commit。

```powershell
# 方法 1：再次 revert revert commit
git revert <revert-commit-hash>

# 方法 2：cherry-pick 原始 commit
git cherry-pick <original-commit-hash>
```

### Q: 如何查看某個 commit 的完整變更？

A: 使用 `git show`：

```powershell
git show <commit-hash>
```

### Q: Revert 會影響其他分支嗎？

A: 不會。Revert 只會影響當前分支。如果需要，可以切換到其他分支執行相同的 revert 操作。

## 參考資源

- [Git 官方文件 - git revert](https://git-scm.com/docs/git-revert)
- [Git 官方文件 - 撤銷變更](https://git-scm.com/book/zh-tw/v2/Git-%E5%B7%A5%E5%85%B7-%E6%92%A4%E9%8A%B7%E8%AE%8A%E6%9B%B4)

