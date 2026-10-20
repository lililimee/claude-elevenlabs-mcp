import os
import uuid
from pathlib import Path

import httpx
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Route
from mcp.server.fastmcp import FastMCP

APP_DIR = Path(__file__).parent
AUDIO_DIR = Path("/tmp/claude-elevenlabs-audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

mcp = FastMCP("ElevenLabs Chinese Voice")

@mcp.tool()
async def speak_text(text: str) -> str:
    """把中文或英文文字转换成 Noah 音色的 MP3，并返回可播放链接。"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "JMVf7JogTKSd7y32YiVG")
    model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
    public_base_url = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")

    if not api_key:
        return "服务还没配置 ElevenLabs API Key。请在 Render 的 Environment Variables 中设置 ELEVENLABS_API_KEY。"
    if not public_base_url:
        return "服务还没配置 PUBLIC_BASE_URL。请设置为 Render 分配给本服务的网址，例如 https://你的服务名.onrender.com。"

    if not text or not text.strip():
        return "请提供需要朗读的文字。"

    endpoint = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = {
        "text": text.strip()[:5000],
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.34,
            "similarity_boost": 0.78,
            "style": 0.55,
            "use_speaker_boost": True
        }
    }
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(endpoint, json=payload, headers=headers)
        if response.status_code >= 400:
            detail = response.text[:700]
            return f"ElevenLabs 返回错误（HTTP {response.status_code}）：{detail}"
        filename = f"{uuid.uuid4().hex}.mp3"
        (AUDIO_DIR / filename).write_bytes(response.content)
        return f"语音已生成。点击或复制这个链接播放：{public_base_url}/audio/{filename}"
    except Exception as exc:
        return f"生成语音时出错：{type(exc).__name__}: {exc}"

async def health(request: Request):
    return JSONResponse({"status": "ok", "service": "ElevenLabs MCP"})

async def audio_file(request: Request):
    filename = request.path_params["filename"]
    # Only allow generated mp3 filenames, preventing path traversal.
    if not filename.endswith(".mp3") or "/" in filename or "\\" in filename:
        return JSONResponse({"error": "not found"}, status_code=404)
    path = AUDIO_DIR / filename
    if not path.is_file():
        return JSONResponse({"error": "音频不存在或服务刚刚重启，请重新生成。"}, status_code=404)
    return FileResponse(path, media_type="audio/mpeg", filename=filename)

app = mcp.streamable_http_app()
app.router.routes.append(Route("/health", health, methods=["GET"]))
app.router.routes.append(Route("/audio/{filename:str}", audio_file, methods=["GET"]))
