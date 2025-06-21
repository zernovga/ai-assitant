from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@app.websocket("/chat")
async def chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()
    await websocket.send_text(f"Message text was: {data}")
