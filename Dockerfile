# 1. เลือก "ระบบปฏิบัติการพื้นฐาน" ที่มี Python 3.11 ติดตั้งมาให้แล้ว
FROM python:3.11-slim

# 2. สร้าง "โฟลเดอร์ทำงาน" ภายในระบบ
WORKDIR /code

# 3. คัดลอก "รายการช้อปปิ้ง" เข้าไปก่อน
COPY ./requirements.txt /code/requirements.txt

# 4. สั่งให้ระบบ "ติดตั้งเครื่องมือ" ทั้งหมดตามรายการ
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 5. คัดลอกไฟล์โปรเจคที่เหลือทั้งหมดเข้าไป
COPY . /code/

# 6. (คำสั่งสุดท้าย) บอกว่าเมื่อเปิดบ้านแล้ว ให้ "สตาร์ทเครื่องยนต์" ด้วยคำสั่งนี้
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]