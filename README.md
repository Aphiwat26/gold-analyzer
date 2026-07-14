# XAUUSD Chart Analyzer — วิเคราะห์กราฟ 3 TF ด้วย Vision AI

เว็บสำหรับอัปโหลดภาพกราฟ 3 ไทม์เฟรม (เช่น H4/H1/M15) แล้วให้ AI วิเคราะห์
จุดเข้า + SL/TP + Risk:Reward + เหตุผล ตามกรอบ multi-timeframe confluence ("สูตรยำ")

## ติดตั้ง
```bash
cd chart-analyzer
pip install -r requirements.txt
```

## รัน
```bash
python server.py
# เปิด http://127.0.0.1:8100
```
- **ยังไม่มี API key:** ใช้งานได้เลยในโหมด **ตัวอย่าง (MOCK)** เห็นหน้าตา + โฟลว์การทำงาน
- **วิเคราะห์ภาพจริง:** ตั้ง key ก่อนรัน
  ```bash
  export ANTHROPIC_API_KEY=sk-ant-...
  python server.py
  ```

## วิธีใช้
1. แคป/อัปโหลดภาพกราฟ 3 ไทม์เฟรม (ใหญ่ → เล็ก) ในช่องที่กำหนด
2. ใส่ราคาปัจจุบัน (ช่วยให้ SL/TP แม่นขึ้นมาก) และโน้ต (เช่น มีข่าว)
3. กด "วิเคราะห์" → ได้ Buy/Sell, Entry, SL, TP, RR, เหตุผลทีละข้อ

## โครงสร้าง
```
server.py     FastAPI (เสิร์ฟหน้าเว็บ + POST /analyze)
analyzer.py   สร้าง prompt + เรียก Claude vision (หรือ mock)
static/index.html   หน้าเว็บอัปโหลด + แสดงผล
```

## หมายเหตุสำคัญ
- AI อ่านกราฟจากภาพได้ แต่**อาจอ่านราคา/สเกลคลาดเคลื่อน** — ใส่ราคาปัจจุบันประกอบเสมอ
- เป็นเครื่องมือช่วยวิเคราะห์เพื่อการศึกษา **ไม่ใช่คำแนะนำการลงทุน** การเทรดทองเสี่ยงสูง
- ปรับโมเดลได้ด้วย env `CLAUDE_MODEL` (ค่าเริ่มต้น claude-sonnet-5)
