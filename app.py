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

def analyze_kline_image(image_path):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        image = Image.open(image_path)
        
        prompt = """
        請分析這張K線圖並提供以下資訊：
        1. 目前的趨勢方向（上漲、下跌、橫盤）
        2. 技術型態分析（如：三角形、旗形、頭肩型等）
        3. 支撐與壓力位分析
        4. 交易量分析（如果圖中有顯示）
        5. 整體市場情緒判斷
        6. 可能的交易建議或風險提醒
        
        請用繁體中文回答，並保持專業且易懂的語調。
        """
        
        response = model.generate_content([prompt, image])
        return response.text
        
    except Exception as e:
        return f"分析圖片時發生錯誤：{str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    analysis_result = None
    uploaded_filename = None
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('請選擇一個檔案')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('請選擇一個檔案')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            analysis_result = analyze_kline_image(filepath)
            uploaded_filename = filename
            
            os.remove(filepath)
            
        else:
            flash('請上傳有效的圖片檔案 (png, jpg, jpeg, gif, bmp, webp)')
    
    return render_template('index.html', 
                         analysis_result=analysis_result,
                         uploaded_filename=uploaded_filename)

@app.errorhandler(413)
def too_large(e):
    flash('檔案大小超過限制 (16MB)')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true')