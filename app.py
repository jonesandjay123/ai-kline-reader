import os
import io
import base64
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
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
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
        
        請分析這些K線圖並用表格格式回答，表格包含以下欄位：
        
        | 股票代號 | 目前位置 | 估計股價 |
        |---------|----------|----------|
        | XXX     | 高點/低點/中間 | $XXX |
        
        要求：
        1. 從檔案名稱中提取股票代號（底線前的部分）
        2. 判斷目前是在相對高點、低點還是中間位置
        3. 根據圖表估計當前大概的股價
        4. 請只回傳表格，不要其他額外說明
        5. 用繁體中文回答
        """
        
        # 組合內容
        content_for_analysis = [prompt] + content_parts
        
        response = model.generate_content(content_for_analysis)
        return response.text
        
    except Exception as e:
        return f"分析圖片時發生錯誤：{str(e)}"

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