# เอาเว็บขึ้นออนไลน์ (ใช้บนมือถือได้ทุกที่)

เมื่อ deploy แล้ว จะได้ลิงก์แบบ `https://xauusd-chart-analyzer.onrender.com`
เปิดจากมือถือที่ไหนก็ได้ ไม่ต้องเปิด Mac ค้าง ไม่ต้อง Wi-Fi เดียวกัน

แนะนำ **Render.com** (มีแพลนฟรี ง่ายสุด) — ไฟล์ที่ต้องใช้เตรียมให้ครบแล้ว
(`Procfile`, `runtime.txt`, `render.yaml`, `requirements.txt`)

## ขั้นตอน

### 1. เอาโค้ดขึ้น GitHub
- สมัคร/ล็อกอิน github.com → สร้าง repo ใหม่ (เช่น `xauusd-chart-analyzer`)
- อัปโหลดไฟล์ทั้งหมดในโฟลเดอร์ `chart-analyzer/` ขึ้น repo
  (ลากไฟล์วางในหน้าเว็บ GitHub ก็ได้ ไม่ต้องใช้ git ก็ยังไหว)

### 2. สร้าง Web Service บน Render
- สมัคร/ล็อกอิน render.com (ล็อกอินด้วย GitHub ได้)
- กด **New +** → **Web Service** → เลือก repo ที่เพิ่งสร้าง
- Render จะอ่าน `render.yaml` ให้เอง (Build/Start command ตั้งไว้แล้ว)
- เลือกแพลน **Free**

### 3. ใส่ API key (ให้วิเคราะห์ภาพจริง)
เลือกอย่างใดอย่างหนึ่ง — ในหน้า service → แท็บ **Environment** → **Add Environment Variable**

**แบบฟรี (แนะนำ) — Google Gemini:**
- ไปที่ **aistudio.google.com** → ล็อกอิน Google → **Get API key** → **Create API key** (ฟรี ไม่ต้องผูกบัตร)
- ที่ Render ใส่ Key: `GEMINI_API_KEY`  Value: `AIza...`

**แบบเสียเงิน — Claude (คุณภาพสูงกว่า):**
- Key: `ANTHROPIC_API_KEY`  Value: `sk-ant-...` (จาก console.anthropic.com)

Save → Render จะ deploy ใหม่อัตโนมัติ (ระบบเลือก Gemini ก่อนถ้ามีทั้งคู่)

### 4. เสร็จ
- ได้ลิงก์ `https://ชื่อ.onrender.com` → เปิดบนมือถือได้เลย
- แคปกราฟทอง 3 TF → อัปโหลด → วิเคราะห์

## ข้อควรรู้
- **แพลนฟรีจะ "หลับ" เมื่อไม่มีคนใช้** ครั้งแรกที่เปิดหลังหลับจะช้า ~30–50 วิ (โหลดตัวเอง) แล้วหลังจากนั้นเร็วปกติ
- **อย่าใส่ API key ลงในโค้ด/GitHub** — ใส่ผ่านหน้า Environment ของ Render เท่านั้น (ไฟล์ `.gitignore` กัน `.env` ไว้แล้ว)
- ถ้าไม่ใส่ key เว็บจะยังรันได้แต่เป็นโหมดตัวอย่าง (MOCK)
- ค่าเรียก Claude API คิดตามการใช้งานจริง ควรตั้งงบ/ลิมิตในบัญชี Anthropic

## ทางเลือกอื่น (ถ้าไม่ใช้ Render)
- **Railway.app** — คล้าย Render ต่อ GitHub แล้วตั้ง env var เหมือนกัน
- **Fly.io / VPS** — ยืดหยุ่นกว่าแต่ตั้งค่ายากขึ้น

> เครื่องมือเพื่อการศึกษา ไม่ใช่คำแนะนำการลงทุน
