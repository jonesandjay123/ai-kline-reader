# AI K線圖分析工具

這是一個使用 Flask 和 Gemini AI 開發的 K 線圖分析網頁應用程式，能夠自動分析股票 K 線圖並提供專業的技術分析建議。

## 功能特色

- 📈 支援多種圖片格式的 K 線圖上傳
- 🤖 整合 Google Gemini Pro 2.5 AI 進行智能分析
- 📱 響應式設計，支援各種裝置
- 🎯 專業的技術分析報告
- 🔒 安全的檔案處理機制

## 系統需求

- Python 3.8+
- Google Gemini API Key

## 安裝步驟

1. **複製專案**
   ```bash
   git clone <repository-url>
   cd ai-kline-reader
   ```

2. **建立虛擬環境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安裝依賴套件**
   ```bash
   pip install -r requirements.txt
   ```

4. **設定環境變數**
   ```bash
   cp .env.example .env
   ```
   
   編輯 `.env` 檔案並填入您的設定：
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key
   SECRET_KEY=your_secret_key_for_flask
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

5. **執行應用程式**
   ```bash
   python app.py
   ```

6. **開啟瀏覽器**
   
   前往 `http://localhost:5000` 開始使用

## 如何取得 Gemini API Key

1. 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登入您的 Google 帳戶
3. 建立新的 API Key
4. 將 API Key 複製到 `.env` 檔案中

## 使用方法

1. **上傳 K 線圖**
   - 點擊「選擇圖片檔案」或直接拖放圖片到上傳區域
   - 支援 PNG, JPG, JPEG, GIF, BMP, WebP 格式
   - 檔案大小限制：16MB

2. **獲得分析結果**
   - 點擊「上傳並分析」按鈕
   - AI 將分析圖片並提供詳細報告
   - 分析內容包括：
     - 趨勢方向分析
     - 技術型態識別
     - 支撐與壓力位
     - 交易量分析
     - 市場情緒判斷
     - 交易建議

## 專案結構

```
ai-kline-reader/
├── app.py                 # Flask 主應用程式
├── requirements.txt       # Python 依賴套件
├── .env.example          # 環境變數範本
├── .gitignore           # Git 忽略檔案
├── templates/
│   └── index.html       # 網頁模板
├── static/
│   ├── css/
│   │   └── style.css    # 自訂樣式
│   └── js/
│       └── script.js    # 前端功能
└── uploads/             # 暫存目錄
```

## 安全性考量

- 上傳的檔案會在分析後自動刪除
- 檔案類型和大小都有嚴格限制
- 使用安全的檔案名稱處理
- API Key 使用環境變數存儲

## 故障排除

### 常見問題

1. **API Key 錯誤**
   - 確認 `.env` 檔案中的 `GEMINI_API_KEY` 正確
   - 檢查 API Key 是否有效且未過期

2. **檔案上傳失敗**
   - 確認檔案格式是否支援
   - 檢查檔案大小是否超過 16MB

3. **分析失敗**
   - 確認網路連線正常
   - 檢查圖片是否清晰可讀

## 技術棧

- **後端**: Flask, Python
- **前端**: HTML5, CSS3, JavaScript, Bootstrap 5
- **AI**: Google Gemini Pro 2.5
- **圖片處理**: Pillow (PIL)
- **環境管理**: python-dotenv

## 授權條款

本專案僅供學習和個人使用。投資有風險，AI 分析結果僅供參考，不構成投資建議。

## 貢獻

歡迎提交 Issue 和 Pull Request 來改善這個專案。

---

**免責聲明**: 本工具提供的分析結果僅供參考，不構成任何投資建議。投資者應該根據自己的判斷做出投資決策，並承擔相應風險。
