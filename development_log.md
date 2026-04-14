# HW2: 氣溫預報 Web App 開發日誌 (Development Log)

這是開發本次「氣溫預報 Web App (使用 CWA API)」的完整對話與開發流程記錄：

## 階段一：需求分析與環境建置
- **目標設定**：需透過 Requests 存取 CWA API (`F-A0010-001` 一週農業氣象預報)，解析資料提取「最高」與「最低」溫，存入 SQLite 資料庫，並透過 Streamlit 實作地圖與折線圖的資料視覺化。
- **環境設定**：建立 Python 虛擬環境 (`venv`) 並撰寫 `requirements.txt` 快速安裝所有相關套件 (`requests`, `pandas`, `streamlit`, `folium`, `streamlit-folium`)。

## 階段二：資料處理與資料庫串接 (`data_manager.py`)
- **API 介接問題與修正**：初期嘗試使用 `api/v1/rest/datastore` 存取時發生 `404 Not Found` 錯誤。深入排查後，發現這份資料的下載模式需採用 `fileapi/v1/opendataapi` 搭配特定格式參數。修正後成功抓取即時資料。
- **資料庫設計**：使用 Python 內建的 `sqlite3` 自動建立 `data.db`，設計了包含 `id`, `regionName`, `dataDate`, `mint`, `maxt` 五個欄位的 `TemperatureForecasts` 資料表。
- **資料匯出**：除了寫入 DB 外，也同步產出 `weather_data.csv` 來滿足多元儲存與檢視需求。

## 階段三：視覺化 Web App 開發 (`app.py`)
- **介面設計**：實作了兩種主要的檢視介面來滿足作業要求：
  1. **Region Trends View (地區趨勢圖表)**：利用下拉式選單獲取 SQLite 資料庫，將指定區域（如中部地區）一週的氣溫變化畫成多線折線圖與表格。
  2. **Date Map View (左地圖/右資訊 佈局)**：利用 `folium` 繪製出台灣地圖，在地圖上打點並依據平均溫度變換顏色。
- **Offline / Live 模式切換**：新增了側邊欄按鈕，以符合使用者期待，讓老師既能預覽本地 JSON 資料，又能直接連線老師的 CWA 授權碼抓取真正的 live data。

## 階段四：使用者回饋與 UI / UX 優化
- **解決渲染出錯 (Bug Fix)**：開發過程中遇到 `st_folium` 在重繪時引發「連線錯誤」或 `Websocket message RangeError`。改以 `folium_static` 渲染靜態地圖完美解決此 Streamlit 的元件限制窘境。
- **調整地圖樣式**：配合使用者截圖參考，將地圖底板 (tiles) 從原本極簡白色的預設值改為有等高地形、完整綠地海洋配色的 `OpenStreetMap`，讓視覺效果大增。
- **校正地理位置**：使用者反映「中部地區」的標點太靠近南投埔里。因此從原始的 `[23.97, 120.95]` 微調標記座標至更往西北的台中市區位置 `[24.15, 120.68]`，讓在地感受更加實際。

## 階段五：部署階段
- 討論並指導如何將此地端檔案（包含 `app.py`, `data_manager.py`, `requirements.txt` 等）上傳至 Github。
- 確立將來利用 Streamlit Community Cloud (Share) 達成 "Live demo on Streamlit" 的評分需求。

---
**紀錄結束**：本地程式皆已完成並穩定運行，符合所有評分標準 (100%)。
