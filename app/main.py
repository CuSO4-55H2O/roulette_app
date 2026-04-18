from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from storage.models import init_db
from roulette.roulette import Manager
import uvicorn
import asyncio

game_manager = Manager()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, group_id: int, user_id: int):
        await websocket.accept()
        if group_id not in self.active_connections:
            self.active_connections[group_id] = {}
        self.active_connections[group_id][user_id] = websocket

    def disconnect(self, group_id: int, user_id: int):
        if group_id in self.active_connections and user_id in self.active_connections[group_id]:
            del self.active_connections[group_id][user_id]
            if not self.active_connections[group_id]:
                del self.active_connections[group_id]

    async def broadcast_public(self, group_id: int, message: str):
        """向群组内所有在线成员广播公开消息"""
        if group_id not in self.active_connections:
            return

        tasks = []
        for user_id, ws in self.active_connections[group_id].items():
            task = asyncio.create_task(self._safe_send(ws, {"type": "public", "content": message}))
            tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def send_private(self, group_id: int, user_id: int, message: str):
        if group_id in self.active_connections and user_id in self.active_connections[group_id]:
            ws = self.active_connections[group_id][user_id]
            await self._safe_send(ws, {"type": "private", "content": message})

    async def _safe_send(self, websocket: WebSocket, data: dict):
        """
        安全发送消息，捕获异常防止任务崩溃。
        """
        try:
            await websocket.send_json(data)
        except Exception:
            pass


ws_manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app):
    init_db()
    print("数据库初始化完成。")
    yield
    pass

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def get_html():
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.websocket("/ws/{group_id}/{user_id}/{nickname}")
async def websocket_endpoint(websocket: WebSocket, group_id: int, user_id: int, nickname: str):
    await ws_manager.connect(websocket, group_id, user_id)
    handler = game_manager.get_handler(group_id)
    await ws_manager.broadcast_public(group_id, f"【系统提示】玩家 {nickname} (ID:{user_id}) 进入了房间。")

    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.broadcast_public(group_id, f"{nickname}: {data}")

            public_msgs = await asyncio.to_thread(
                handler.process, user_id, data, nickname
            )

            if public_msgs:
                for msg in public_msgs:
                    await ws_manager.broadcast_public(group_id, f"【系统】\n{msg}")

            private_msgs = handler.fetch_flush_private()
            if private_msgs:
                for target_user_id, p_msg in private_msgs:
                    await ws_manager.send_private(group_id, target_user_id, f"【私聊系统】\n{p_msg}")

    except WebSocketDisconnect:
        ws_manager.disconnect(group_id, user_id)
        await ws_manager.broadcast_public(group_id, f"【系统提示】玩家 {nickname} 离开了房间。")

if __name__=='__main__':
    uvicorn.run(app,port=8000,host='127.0.0.1')