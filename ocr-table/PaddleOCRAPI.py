import io
import paddleocr
import json
import base64
from flask import Flask, request, jsonify, render_template
import numpy as np
from PIL import Image

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['JSON_AS_ASCII'] = False

ppocr = paddleocr.PaddleOCR(use_gpu=False)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/PaddleOCR/DetectText", methods=["POST"])
def PaddleOCR():
    if not request.data:
        return jsonify({"error": "request data is null"}), 400
    
    try:
        # 获取并解码图片
        data = json.loads(request.data)
        img_bytes = base64.b64decode(data)
        image = io.BytesIO(img_bytes)
        temp = Image.open(image)
        img = np.array(temp)[:, :, :3]
        
        # 执行OCR
        info = ppocr.ocr(img)
        
        # 格式化结果
        result = {"TextBlocks": []}
        for textblocks in info:
            textBlock = {"Points": [], "Text": ""}
            for tk in textblocks[0]:
                point = {"x": float(tk[0]), "y": float(tk[1])}
                textBlock["Points"].append(point)
            textBlock["Text"] = textblocks[1][0]
            result["TextBlocks"].append(textBlock)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def main():
    app.run(debug=True, host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()