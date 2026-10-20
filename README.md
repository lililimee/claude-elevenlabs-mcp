# Claude + ElevenLabs MCP 语音服务

这个项目提供一个远程 MCP 工具 `speak_text`：把文字交给 ElevenLabs 合成 MP3，并返回可点击的播放链接。

## 部署到 Render

1. 将这些文件上传到一个 GitHub 仓库。
2. 在 Render 选择 **New Web Service**，连接这个仓库。
3. 部署成功后，记下 Render 分配的网址，例如 `https://你的服务名.onrender.com`。
4. 在 Render 服务的 **Environment** 页面添加：
   - `ELEVENLABS_API_KEY`：你的 ElevenLabs API Key（保密，不要放进 GitHub）
   - `ELEVENLABS_VOICE_ID`：`JMVf7JogTKSd7y32YiVG`
   - `PUBLIC_BASE_URL`：Render 分配给你的完整网址，例如 `https://你的服务名.onrender.com`
   - `ELEVENLABS_MODEL_ID`：`eleven_multilingual_v2`
5. 保存并重新部署。

## MCP 地址

远程 MCP endpoint 是：

`https://你的服务名.onrender.com/mcp`

把这个地址添加到支持远程 MCP 的客户端中。

## 重要说明

- 这个工具会生成音频链接；它不能强制 Claude Android App 自动播放。通常需要点击工具返回的链接。
- Render 免费服务可能休眠；临时文件也可能在重启后消失。若链接失效，请重新生成语音。
- 不要把 API Key 提交到 GitHub 或发送给任何人。
