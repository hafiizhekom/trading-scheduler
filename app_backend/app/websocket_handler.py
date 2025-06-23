# app/websocket_handler.py
from fastapi import WebSocket, WebSocketDisconnect
import json
import logging

logger = logging.getLogger(__name__)

active_connections = {}  # shared dictionary untuk semua koneksi

async def handle_websocket(websocket: WebSocket, symbol: str):
    await websocket.accept()
    logger.info(f"[WS] New connection for {symbol}")
    
    if symbol not in active_connections:
        active_connections[symbol] = []
    active_connections[symbol].append(websocket)
    
    logger.info(f"[WS] Active connections for {symbol}: {len(active_connections[symbol])}")

    try:
        while True:
            # Keep connection alive
            message = await websocket.receive_text()
            logger.debug(f"[WS] Received message from {symbol} client: {message}")
            
    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected from {symbol}")
        if websocket in active_connections.get(symbol, []):
            active_connections[symbol].remove(websocket)
            
        if symbol in active_connections and not active_connections[symbol]:
            del active_connections[symbol]
            logger.info(f"[WS] No more connections for {symbol}, removed from active_connections")
            
    except Exception as e:
        logger.error(f"[WS] Error in websocket handler for {symbol}: {e}")
        if websocket in active_connections.get(symbol, []):
            active_connections[symbol].remove(websocket)

async def broadcast_to_clients(symbol, payload):
    connections = active_connections.get(symbol, [])
    logger.info(f"[WS] Broadcasting to {len(connections)} clients for {symbol}")
    
    if not connections:
        logger.warning(f"[WS] No active connections for {symbol}")
        return
    
    # Copy list to avoid modification during iteration
    connections_copy = connections.copy()
    
    for ws in connections_copy:
        try:
            await ws.send_text(json.dumps(payload))
            logger.debug(f"[WS] Successfully sent data to {symbol} client")
        except Exception as e:
            logger.error(f"[WS] Failed to send to {symbol} client: {e}")
            # Remove broken connection
            if ws in active_connections.get(symbol, []):
                active_connections[symbol].remove(ws)