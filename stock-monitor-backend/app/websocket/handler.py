from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.stock_subscriptions: dict[WebSocket, set[int]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        self.stock_subscriptions[websocket] = set()

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        self.stock_subscriptions.pop(websocket, None)

    async def subscribe_stock(self, websocket: WebSocket, stock_id: int):
        if websocket in self.stock_subscriptions:
            self.stock_subscriptions[websocket].add(stock_id)

    async def unsubscribe_stock(self, websocket: WebSocket, stock_id: int):
        if websocket in self.stock_subscriptions:
            self.stock_subscriptions[websocket].discard(stock_id)

    async def broadcast_stock_data(self, stock_id: int, data: dict):
        for websocket, subscriptions in self.stock_subscriptions.items():
            if stock_id in subscriptions:
                try:
                    await websocket.send_json({
                        'type': 'stock_update',
                        'stock_id': stock_id,
                        'data': data
                    })
                except:
                    self.disconnect(websocket)

manager = ConnectionManager()

@router.websocket("/realtime")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()

            if data.get('action') == 'subscribe':
                await manager.subscribe_stock(websocket, data.get('stock_id'))

            elif data.get('action') == 'unsubscribe':
                await manager.unsubscribe_stock(websocket, data.get('stock_id'))

            elif data.get('action') == 'ping':
                await websocket.send_json({'type': 'pong'})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
