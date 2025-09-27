# ======================================================================
#  API ตรวจจับความเบลอ (Blur Detector API)
#  เวอร์ชัน Single Threshold
# ======================================================================

from flask import Flask, request, jsonify
import cv2
import numpy as np
import os

# ----------------------------------------------------------------------
# สร้าง Flask App
# ----------------------------------------------------------------------
app = Flask(__name__)

# ----------------------------------------------------------------------
# ฟังก์ชันคำนวณค่า blur_score ด้วย Laplacian Variance
# ยิ่งค่ามาก → ภาพยิ่งชัด (มีรายละเอียดเส้นขอบเยอะ)
# ยิ่งค่าน้อย → ภาพยิ่งเบลอ
# ----------------------------------------------------------------------
def calculate_laplacian_variance(image_bytes):
    image_np = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    if img is None:
        return 0
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance

# ----------------------------------------------------------------------
# Endpoint หลักสำหรับตรวจภาพเบลอ
# ใช้ POST /predict พร้อมส่งไฟล์ภาพ (multipart/form-data)
# ----------------------------------------------------------------------
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'ไม่พบไฟล์ใน request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'ไม่ได้เลือกไฟล์สำหรับอัปโหลด'}), 400

    if file:
        image_bytes = file.read()
        score = calculate_laplacian_variance(image_bytes)

        # ✅ Threshold (ปรับตาม dataset ที่คุณรันได้)
        threshold = 400   # ถ้าภาพชัดเยอะเกินไปให้ลองขยับเป็น 500
        prediction = "blurry" if score < threshold else "clear"

        return jsonify({
            'prediction': prediction,
            'blur_score': score,
            'threshold': threshold
        })

# ----------------------------------------------------------------------
# Endpoint สำหรับตรวจว่า API ทำงานอยู่หรือไม่
# ----------------------------------------------------------------------
@app.route('/', methods=['GET'])
def health_check():
    return "Blur Detector API (Single Threshold) กำลังทำงาน!"

# ----------------------------------------------------------------------
# รัน Flask App (ใช้สำหรับทดสอบ local)
# ถ้า deploy ไป Render/HF Space ให้ใช้ gunicorn app:app แทน
# ----------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
