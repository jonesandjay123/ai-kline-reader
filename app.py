import os
import io
import base64
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_multiple_kline_images(image_files_info):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 準備圖片和檔案名稱資訊
        content_parts = []
        file_info_text = "以下是要分析的K線圖檔案：\n"
        
        for info in image_files_info:
            filename = info['filename']
            filepath = info['filepath']
            
            # 從檔名提取股票代號
            stock_symbol = filename.split('_')[0] if '_' in filename else filename.split('.')[0]
            file_info_text += f"- {filename} (股票代號: {stock_symbol})\n"
            
            # 載入圖片
            image = Image.open(filepath)
            content_parts.append(image)
        
        prompt = f"""
        {file_info_text}
        
        請分析這些K線技術分析走勢圖並用表格格式回答，表格包含以下欄位：
        
        | 圖片檔案名 | 股票代號 | 時間區間 | 當前走勢 |
        |-----------|----------|----------|----------|
        | NVDA_3h.png | NVDA | 3h | 多 |
        | NVDA_day.png | NVDA | 1d | 空 |
        
        要求：
        1. 從檔案名稱格式 `股票代號_時間區間.png` 中提取資訊：
           - 股票代號：底線前的部分（如：NVDA、TSM）
           - 時間區間：底線後到 .png 前的部分，並轉換格式：
             * `3h` = 3h（近三小時）
             * `day` = 1d（近一天）  
             * `week` = 1w（近一週）
        2. 重點分析圖中**最右邊的價格走勢**，判斷趨勢：
           - 「多」= bullish，上漲趨勢
           - 「空」= bearish，下跌趨勢
        3. 不需要輸出股價數字，也不需要判斷是否為高點/低點
        4. 請只回傳完整表格，不要其他額外說明
        5. 用繁體中文回答
        """
        
        # 組合內容
        content_for_analysis = [prompt] + content_parts
        
        response = model.generate_content(content_for_analysis)
        return response.text
        
    except Exception as e:
        return f"分析圖片時發生錯誤：{str(e)}"

def extract_date_from_filename(filename):
    """從檔名中提取日期信息"""
    # 尋找日期格式，如 YYYYMMDD 或 YYYY-MM-DD 或 YYYY_MM_DD
    date_patterns = [
        r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})',  # YYYYMMDD, YYYY-MM-DD, YYYY_MM_DD
        r'(\d{4})[-_]?(\d{1,2})[-_]?(\d{1,2})'  # 也支援單數字日期
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, filename)
        if match:
            year, month, day = match.groups()
            try:
                # 補零確保格式一致
                formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                return formatted_date
            except:
                continue
    
    # 如果找不到日期，返回今天的日期
    return datetime.now().strftime("%Y-%m-%d")

def send_analysis_email(analysis_result, uploaded_files):
    """發送分析結果郵件"""
    try:
        # 檢查郵件功能是否啟用
        email_enabled = os.getenv('EMAIL_ENABLED', 'False').lower() == 'true'
        if not email_enabled:
            print("郵件功能未啟用")
            return False
        
        # 讀取郵件配置
        email_host = os.getenv('EMAIL_HOST')
        email_port = int(os.getenv('EMAIL_PORT', 587))
        email_use_tls = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
        email_username = os.getenv('EMAIL_USERNAME')
        email_password = os.getenv('EMAIL_PASSWORD')
        email_from = os.getenv('EMAIL_FROM')
        email_to = os.getenv('EMAIL_TO')
        
        if not all([email_host, email_username, email_password, email_from, email_to]):
            print("郵件配置不完整")
            return False
        
        # 從上傳的檔案中提取日期
        analysis_date = datetime.now().strftime("%Y-%m-%d")
        if uploaded_files:
            # 嘗試從第一個檔案名稱中提取日期
            analysis_date = extract_date_from_filename(uploaded_files[0])
        
        # 建立郵件內容
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = email_to
        msg['Subject'] = f"K線圖技術分析報告 - {analysis_date}"
        
        # 郵件正文
        body = f"""
親愛的投資者，

以下是您上傳的K線圖技術分析結果：

分析日期：{analysis_date}
上傳檔案：{', '.join(uploaded_files) if uploaded_files else '無'}

--- 分析結果 ---
{analysis_result}

本報告由AI系統自動生成，僅供參考，請謹慎投資。

祝好
K線分析系統
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 發送郵件
        server = smtplib.SMTP(email_host, email_port)
        if email_use_tls:
            server.starttls()
        server.login(email_username, email_password)
        text = msg.as_string()
        server.sendmail(email_from, email_to, text)
        server.quit()
        
        print(f"郵件已成功發送至 {email_to}")
        return True
        
    except Exception as e:
        print(f"發送郵件時發生錯誤：{str(e)}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    analysis_result = None
    uploaded_files = None
    
    if request.method == 'POST':
        if 'files' not in request.files:
            flash('請選擇檔案')
            return redirect(request.url)
        
        files = request.files.getlist('files')
        
        if not files or all(file.filename == '' for file in files):
            flash('請選擇至少一個檔案')
            return redirect(request.url)
        
        # 處理多個檔案
        image_files_info = []
        uploaded_filenames = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                image_files_info.append({
                    'filename': filename,
                    'filepath': filepath
                })
                uploaded_filenames.append(filename)
            else:
                flash(f'檔案 {file.filename} 格式不支援')
        
        if image_files_info:
            # 分析所有圖片
            analysis_result = analyze_multiple_kline_images(image_files_info)
            uploaded_files = uploaded_filenames
            
            # 發送分析結果郵件
            if analysis_result and not analysis_result.startswith("分析圖片時發生錯誤"):
                email_sent = send_analysis_email(analysis_result, uploaded_files)
                if email_sent:
                    flash('分析完成，結果已發送至您的郵箱！', 'success')
                else:
                    flash('分析完成，但郵件發送失敗。請檢查郵件配置。', 'warning')
            
            # 清理暫存檔案
            for info in image_files_info:
                try:
                    os.remove(info['filepath'])
                except:
                    pass
        else:
            flash('請上傳有效的圖片檔案 (png, jpg, jpeg, gif, bmp, webp)')
    
    return render_template('index.html', 
                         analysis_result=analysis_result,
                         uploaded_files=uploaded_files)

@app.errorhandler(413)
def too_large(e):
    flash('檔案大小超過限制 (16MB)')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true')