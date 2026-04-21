from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from telethon.sync import TelegramClient
from telethon.tl.types import InputMessageID
import os, io

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["SESSION_STRING"]

app = FastAPI()
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

@app.on_event("startup")
async def startup():
    await client.connect()

@app.get("/download/{message_id}")
async def download(message_id: int):
    msg = await client.get_messages("me", ids=message_id)
    if not msg or not msg.document:
        return {"error": "arquivo não encontrado"}
    buf = io.BytesIO()
    await client.download_media(msg, buf)
    buf.seek(0)
    nome = message_id
    for attr in msg.document.attributes:
        if hasattr(attr, "file_name"):
            nome = attr.file_name
    return StreamingResponse(buf, media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={nome}"})
