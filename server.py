"""
Chart Analyzer Backend — FastAPI
รับภาพกราฟ 3 TF + ราคา แล้วส่งให้ analyzer วิเคราะห์

รัน:  python server.py    แล้วเปิด http://127.0.0.1:8100
ใส่ key จริง:  export ANTHROPIC_API_KEY=sk-ant-...   ก่อนรัน
"""
from __future__ import annotations
import os
import sys

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from analyzer import analyze  # noqa: E402

app = FastAPI(title="XAUUSD Chart Analyzer")


@app.get("/")
def index():
    return FileResponse(os.path.join(HERE, "static", "index.html"))


@app.post("/analyze")
async def do_analyze(
    tf_high: UploadFile = File(...),
    tf_mid: UploadFile = File(...),
    tf_low: UploadFile = File(...),
    symbol: str = Form("XAUUSD"),
    price: str = Form(""),
    notes: str = Form(""),
    label_high: str = Form("H4"),
    label_mid: str = Form("H1"),
    label_low: str = Form("M15"),
):
    images = []
    for up, label in ((tf_high, label_high), (tf_mid, label_mid), (tf_low, label_low)):
        data = await up.read()
        images.append({
            "label": label,
            "media_type": up.content_type or "image/png",
            "data": data,
        })
    try:
        result = analyze(images, {"symbol": symbol, "price": price, "notes": notes})
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


app.mount("/static", StaticFiles(directory=os.path.join(HERE, "static")), name="static")


if __name__ == "__main__":
    import socket
    import uvicorn
    # PORT: โฮสต์ออนไลน์ (Render ฯลฯ) จะกำหนดผ่าน env, ในเครื่องใช้ 8100
    port = int(os.environ.get("PORT", 8100))
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        ip = "IP-ของเครื่อง"
    print("=" * 48)
    print(f"  เปิดในเครื่องนี้ :  http://127.0.0.1:{port}")
    print(f"  เปิดจากมือถือ   :  http://{ip}:{port}  (ต่อ Wi-Fi เดียวกัน)")
    print("=" * 48)
    uvicorn.run(app, host="0.0.0.0", port=port)
