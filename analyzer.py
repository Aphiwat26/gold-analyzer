"""
Chart Analyzer — วิเคราะห์ภาพกราฟ 3 ไทม์เฟรม ด้วย Vision AI (Claude)
คืนจุดเข้า + SL/TP + เหตุผล ตามกรอบ "สูตรยำ" confluence

- ถ้ามี ANTHROPIC_API_KEY → เรียก Claude vision จริง
- ถ้าไม่มี → คืนผลตัวอย่าง (mock) เพื่อดูโฟลว์/หน้าตา
"""
from __future__ import annotations
import base64
import json
import os
import re

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")

SYSTEM_PROMPT = """คุณเป็นนักวิเคราะห์เทคนิคทองคำ (XAUUSD) ผู้เชี่ยวชาญ
วิเคราะห์ภาพกราฟ 3 ไทม์เฟรมที่ให้มา (เรียงจากใหญ่ไปเล็ก) ตามกรอบ multi-timeframe confluence:
- TF ใหญ่ (เช่น H4): หาเทรนด์หลัก (ทิศทาง)
- TF กลาง (เช่น H1): โครงสร้างตลาด (HH/HL หรือ LL/LH), แนวรับ-ต้าน
- TF เล็ก (เช่น M15): จังหวะเข้า (ย่อเข้าโซน, แท่งเทียนยืนยัน)
ประเมินความมั่นใจเป็นคะแนน 0-100 ถ้าคอนฟลูเอนซ์ไม่พอให้ตอบ NEUTRAL

ตอบกลับเป็น JSON เท่านั้น (ห้ามมีข้อความอื่นนอก JSON) ตามสคีมา:
{
  "bias": "BUY" | "SELL" | "NEUTRAL",
  "confidence": 0-100,
  "entry": number|null,
  "stop_loss": number|null,
  "take_profit": number|null,
  "risk_reward": number|null,
  "key_levels": [number, ...],
  "reasons": ["เหตุผลภาษาไทยทีละข้อ", ...],
  "warnings": ["ข้อควรระวัง เช่น อ่านสเกลจากภาพอาจคลาดเคลื่อน", ...]
}
กฎ: SL/TP ต้องสมเหตุผลกับราคาปัจจุบัน, Risk:Reward ควร >= 1.5, ระบุเหตุผลอิงสิ่งที่เห็นจริงในภาพ
ถ้าผู้ใช้ให้ราคาปัจจุบัน/แนวสำคัญมา ให้ยึดค่านั้นเป็นหลักในการคำนวณ"""


def _mock():
    return {
        "bias": "BUY",
        "confidence": 72,
        "entry": 4080.0,
        "stop_loss": 4068.0,
        "take_profit": 4104.0,
        "risk_reward": 2.0,
        "key_levels": [4068.0, 4080.0, 4104.0],
        "reasons": [
            "(ตัวอย่าง MOCK) H4 อยู่เหนือ EMA เทรนด์ = โครงสร้างหลักขาขึ้น",
            "H1 ทำ Higher-High / Higher-Low ต่อเนื่อง ยืนยันเทรนด์",
            "M15 ราคาย่อมาที่แนวรับ 4080 แล้วเกิดแท่งกลับตัว",
            "ตั้ง SL ใต้แนวรับ, TP ที่แนวต้านถัดไป ได้ RR ~2.0",
        ],
        "warnings": [
            "นี่คือผลตัวอย่าง (ยังไม่ได้ตั้ง ANTHROPIC_API_KEY)",
            "การอ่านราคาจากภาพอาจคลาดเคลื่อน ควรใส่ราคาปัจจุบันประกอบ",
        ],
        "mock": True,
    }


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError("ไม่พบ JSON ในคำตอบของโมเดล")
    return json.loads(m.group(0))


def _ctx_text(context: dict) -> str:
    return (f"สัญลักษณ์: {context.get('symbol','XAUUSD')}\n"
            f"ราคาปัจจุบัน: {context.get('price') or '(ไม่ระบุ)'}\n\n"
            "วิเคราะห์และตอบเป็น JSON ตามสคีมา")


def _gemini(images, context, api_key):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=api_key)
    parts = []
    for img in images:
        parts.append(f"ไทม์เฟรม: {img['label']}")
        parts.append(types.Part.from_bytes(data=img["data"], mime_type=img["media_type"]))
    parts.append(_ctx_text(context))
    resp = client.models.generate_content(
        model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=parts,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )
    result = _extract_json(resp.text)
    result["mock"] = False
    result["provider"] = "gemini"
    return result


def _claude(images, context, api_key):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    content = []
    for img in images:
        content.append({"type": "text", "text": f"ไทม์เฟรม: {img['label']}"})
        content.append({"type": "image", "source": {
            "type": "base64", "media_type": img["media_type"],
            "data": base64.standard_b64encode(img["data"]).decode()}})
    content.append({"type": "text", "text": _ctx_text(context)})
    msg = client.messages.create(
        model=MODEL, max_tokens=1500, system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}])
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    result = _extract_json(text)
    result["mock"] = False
    result["provider"] = "claude"
    return result


def analyze(images: list[dict], context: dict) -> dict:
    """
    images: [{"label": "H4", "media_type": "image/png", "data": bytes}, ...]
    context: {"symbol": "...", "price": "..."}
    เลือกผู้ให้บริการอัตโนมัติ: Gemini (ฟรี) > Claude > mock
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    claude_key = os.environ.get("ANTHROPIC_API_KEY")
    try:
        if gemini_key:
            return _gemini(images, context, gemini_key)
        if claude_key:
            return _claude(images, context, claude_key)
        return _mock()
    except ImportError as e:
        print(f"[analyze] import error: {e}")
        return {**_mock(), "warnings": [f"ยังไม่ได้ติดตั้งไลบรารี: {e}"]}
    except Exception as e:
        print(f"[analyze] error: {e}")   # ให้เห็นใน Render Logs เวลาดีบัก
        return {**_mock(), "warnings": [f"เรียก AI ไม่สำเร็จ: {e}", "แสดงผลตัวอย่างแทน"]}
