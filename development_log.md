# HW2: 氣溫預報 Web App 開發日誌 (Q&A 形式)

本文件紀錄了開發「氣溫預報 Web App (使用 CWA API)」過程中，使用者 (User) 與 AI 修改與討論的重點紀錄。

---

### 🟢 階段一：專案初始化與環境建置

**User**: 「我想做一個 HW2 氣溫預報 Web App，需要用 CWA API 抓一週資料，存到 SQLite，最後用 Streamlit 做出來。能幫我完成嗎？」

**AI**: 「沒問題。首先我幫你建置了 Python 虛擬環境，並撰寫了 `requirements.txt` 包含 `requests`, `pandas`, `streamlit`, `folium` 等套件。接著我幫你設計了 `data_manager.py` 來處理後端資料，以及 `app.py` 處理前端視覺化。」

---

### 🟢 階段二：後端資料抓取與 API 修正

**User**: 「CWA 的連結好像連不上，即時更新功能噴錯了 (404 Error)？」

**AI**: 「檢查後發現，這份農業氣象預報資料 (`F-A0010-001`) 無法使用傳統的 `datastore` 路徑。我幫你將網址改為 `fileapi` 下載模式，並補上 `downloadType=WEB&format=JSON` 參數，現在點擊 Refresh 已經可以抓到最新資料並存入 `data.db` 資料庫了。」

---

### 🟢 階段三：前端視覺化與地圖優化

**User**: 「地圖顯示不出來，出現 `not connected to a server!` 或 `Websocket error` 是什麼原因？」

**AI**: 「這是因為 `streamlit-folium` 套件在某些 Streamlit 版本中與 Websocket 連線衝突。我幫你將渲染方式改為 `folium_static`，這能保證地圖在雲端伺服器上也能穩定顯示。」

**User**: 「地圖可以再漂亮一點嗎？我想要彩色一點、有等高線的那種風景底圖。」

**AI**: 「好的。我幫你將地圖底圖從灰白的 `CartoDB positron` 改成了色彩豐富且具有地形感的 `OpenStreetMap`，看起來會更專業。」

---

### 🟢 階段四：細節調整與地理校正

**User**: 「地圖上的『中部地區』標點好像太偏南投了，可以靠近台中一點嗎？」

**AI**: 「我已經將中部地區的座標從南投中心點調整為台中市區經緯度 (`24.15, 120.68`)，現在標記點更符合大眾對中部的印象了。」

---

### 🟢 階段五：GitHub 推送與雲端部署

**User**: 「我需要部署到 Streamlit Community Cloud 嗎？怎麼操作？」

**AI**: 「是的，作業規範需要 Live Demo。我幫你撰寫了 `README.md` 詳細說明安裝步驟，並教你設定 GitHub Repository。最後我們成功將程式碼推送到 GitHub，並完成線上部署。」

**User**: 「幫我紀錄對話過程存成 log，我想用『我問你答』的形式呈現。」

**AI**: 「沒問題，這份開發日誌已更新為問答互動模式，方便老師閱讀你的思考與修正過程。」

---

**紀錄結束**：本專案已完全符合作業要求，包含 GitHub 連結、Streamlit 線上網址、SQLite 資料庫整合與開發紀錄。
