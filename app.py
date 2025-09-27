# ======================================================================
#  API ตรวจจับความเบลอ (Blur Detector API)
#  เวอร์ชันนี้ใช้ threshold ตัดสิน ไม่ได้ใช้โมเดลที่เทรนไว้ (.joblib)
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
    # แปลงไฟล์ภาพจาก bytes เป็น array
    image_np = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    if img is None:
        return 0  # ถ้าอ่านไฟล์ไม่ได้ ให้คืนค่า 0

    # แปลงภาพเป็น grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # คำนวณค่า Laplacian Variance
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance

# ----------------------------------------------------------------------
# Endpoint หลักสำหรับตรวจภาพเบลอ
# ใช้ POST /predict พร้อมส่งไฟล์ภาพ (multipart/form-data)
# ----------------------------------------------------------------------
@app.route('/predict', methods=['POST'])
def predict():
    # ตรวจสอบว่ามีไฟล์ถูกส่งมาหรือไม่
    if 'file' not in request.files:
        return jsonify({'error': 'ไม่พบไฟล์ใน request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'ไม่ได้เลือกไฟล์สำหรับอัปโหลด'}), 400

    if file:
        # อ่านไฟล์เป็น bytes
        image_bytes = file.read()

        # คำนวณ blur_score
        score = calculate_laplacian_variance(image_bytes)

        # --------------------------------------------------------------
        # ✅ ปรับ threshold ตรงนี้ได้เลย
        # ค่า threshold ที่เหมาะสม: 
        #   - < 100 → เบลอ
        #   - > 150 → ชัด
        # (ขึ้นกับ dataset ของคุณ สามารถทดลองปรับได้เอง)
        # --------------------------------------------------------------
        threshold = 150  
        prediction = "blurry" if score < threshold else "clear"

        # ส่งผลลัพธ์กลับเป็น JSON
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
    return "Blur Detector API กำลังทำงาน!"

# ----------------------------------------------------------------------
# รัน Flask App (ใช้สำหรับทดสอบ local)
# ถ้า deploy ไป Render/HF Space ให้ใช้ gunicorn app:app แทน
# ----------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
