from flask import Flask, request, render_template, jsonify
import whisper
import os
import tempfile
import time
import uuid

app = Flask(__name__)

# 确保上传目录存在
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 全局变量存储已加载的模型
loaded_models = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': '没有上传音频文件'}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取模型名称，默认为 base
    model_name = request.form.get('model', 'base')
    if model_name not in ['tiny', 'base', 'small', 'medium', 'large']:
        return jsonify({'error': '无效的模型名称'}), 400
    
    # 保存上传的文件
    filename = str(uuid.uuid4()) + os.path.splitext(audio_file.filename)[1]
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    audio_file.save(filepath)
    
    try:
        # 加载模型（如果尚未加载）
        if model_name not in loaded_models:
            start_time = time.time()
            loaded_models[model_name] = whisper.load_model(model_name)
            load_time = time.time() - start_time
        else:
            load_time = 0
        
        model = loaded_models[model_name]
        
        # 转录音频
        start_time = time.time()
        result = model.transcribe(filepath, language="zh")
        transcribe_time = time.time() - start_time
        
        # 返回结果
        return jsonify({
            'text': result['text'],
            'load_time': f"{load_time:.2f}秒" if load_time > 0 else "模型已预加载",
            'transcribe_time': f"{transcribe_time:.2f}秒"
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # 清理临时文件
        try:
            os.remove(filepath)
        except:
            pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)