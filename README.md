# HW2: Temperature Forecast Web App 🌤️

**Live Demo URL:** [https://kungtan-aiot-hm2-temp-forecast.streamlit.app/](https://kungtan-aiot-hm2-temp-forecast.streamlit.app/)

這是一個基於中央氣象署 (CWA) 開放資料 API 所開發的氣溫預報視覺化 Web 應用程式。本專案將一週的農漁業氣象預報資料抓取下來後，寫入 SQLite 資料庫中，最後使用 Streamlit 建立一個能與使用者互動的數據儀表板，包含動態地圖與氣溫趨勢圖。

---

## 🚀 專案功能特色 (Features)

1. **即時 / 離線資料獲取 (`data_manager.py`)**：
   - 使用 `requests` 套件介接 CWA API，解析包含北部、中部、南部、東北部、東部及東南部地區的一週氣溫預報。
   - 支援備用存取機制：允許在離線狀態下讀取本地 `F-A0010-001.json` 檔案。
2. **SQLite3 資料庫整合**：
   - 將讀取、解析過後的最高溫 (MaxT) 與最低溫 (MinT) 等資料，寫入至名為 `data.db` 的資料庫。
   - 資料表 `TemperatureForecasts` 保存所有檢索需要的歷史與即時查詢依據。
3. **Streamlit 視覺化前端 (`app.py`)**：
   - **區域趨勢檢視 (Region Trends View)**：透過下拉選單選擇特定地區，直接查詢資料庫並繪製出一週氣溫變化折線圖以及詳細報表。
   - **地圖檢視 (Date Map View)**：結合 HTML 排版與 `folium`，提供左側地圖、右側表格佈局。在地圖上打點並以顏色區分平均氣溫的冷熱狀況 (<20°C 藍色, 20-25°C 綠色, 25-30°C 橘金, >30°C 紅色)。

---

## 📂 專案檔案結構 (Project Structure)

```
d:\aiot_hm2_g\
│
├── app.py                   # Streamlit 前端 Web App 主程式
├── data_manager.py          # 後端爬蟲、JSON解析與 SQLite 資料庫操作模組
├── data.db                  # 系統自動建立的 SQLite 資料庫檔案
├── weather_data.csv         # 系統自動導出的預測資料備份
├── requirements.txt         # 執行此專案所需的 Python 依賴包
├── F-A0010-001.json         # 氣象局預報的備用離線資料集
├── development_log.md       # 本專案的開發與 debug 過程記錄檔
└── README.md                # 專案說明文件 (也就是本檔案)
```

---

## 🛠️ 安裝與環境建置 (Installation)

1. 請先確保你的環境已經安裝了 Python (推薦 Python 3.9 以上版本)。
2. 透過指令切換到本專案目錄下：
   ```bash
   cd d:\aiot_hm2_g
   ```
3. 建立並啟動 Python 虛擬環境：
   ```powershell
   python -m venv venv
   # 在 Windows 環境下啟動：
   .\venv\Scripts\Activate.ps1
   ```
4. 安裝依賴套件 (Dependencies)：
   ```bash
   pip install -r requirements.txt
   ```

---

## 📖 如何使用 (Usage)

### 方法 1: 啟動 Streamlit Web App (推薦)
啟動虛擬環境後，直接在終端機輸入：
```bash
streamlit run app.py
```
執行後，如果沒有跳出瀏覽器，可以自行打開畫面中顯示的 `Local URL` (通常是 `http://localhost:8501`)。
網頁左側有 **Data Controls** 選單，你可以切換「Local JSON (Offline)」或是「CWA API (Live)」模式。

> [!IMPORTANT]
> **資料更新機制**：當切換不同的資料模式 (Local JSON / CWA API) 後，請務必點擊下方的 **Refresh Data** 按鈕。系統才會真正去讀取對應的檔案或連結，並覆蓋原本的資料庫來更新畫面上的氣溫與日期！

### 方法 2: 獨立測試後端資料抓取
如果你想針對後端抓資料以及寫入資料庫這段邏輯單獨做測試，可以執行：
```bash
python data_manager.py
```
程式會從 API (或本地的 json) 解析檔案，並印出所有存在資料庫當中的地區清單與「中部地區」的詳細明細，以供驗證。

---

## 💡 注意事項

* 如果在 Windows PowerShell 無法執行 `Activate.ps1`，可能需要以管理員身分開啟 PowerShell 並解開權限限制 (`Set-ExecutionPolicy Unrestricted`)。
* 部署至 [Streamlit Community Cloud](https://share.streamlit.io/) 時，請一併將 GitHub repository 設定指向 `app.py` 即可獲得你的 Live Demo 網址。
