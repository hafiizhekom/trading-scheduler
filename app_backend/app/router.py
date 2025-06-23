# app/router.py

from fastapi import APIRouter, WebSocket
from app.websocket_handler import handle_websocket

router = APIRouter()

@router.websocket("/ws/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await handle_websocket(websocket, symbol)

__all__ = ["router"]
