import logging
import os
from contextlib import asynccontextmanager
from json import load

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket

from .chatbot import build_graph

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        logger.info("Loading agent configuration from /run/secrets/agent_config")
        os.environ.update(load(open("/run/secrets/agent_config")))
        logger.info("Agent configuration loaded successfully.")

    global graph
    graph = build_graph()

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@app.websocket("/chat")
async def chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    user_input = await websocket.receive_text()
    response = graph.invoke({"messages": [{"role": "user", "content": user_input}]})
    await websocket.send_text(response["messages"][-1].content)
    await websocket.close()


@app.get("/chat_response")
async def chat_response(data: str):
    response = graph.invoke({"messages": [{"role": "user", "content": data}]})
    return response["messages"][-1].content
