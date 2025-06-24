# app/websocket_handler.py
from fastapi import WebSocket, WebSocketDisconnect
import json
import logging

logger = logging.getLogger(__name__)

active_connections = {}  # Format: {channel_key: [websocket_connections]}

async def handle_websocket(websocket: WebSocket, channel_key: str, asset_type: str, symbol: str):
    """
    Handle WebSocket connection for different asset types
    
    Args:
        websocket: WebSocket connection
        channel_key: Unique key for this channel (e.g., "crypto:BTC-USD", "gold", "forex:USD")
        asset_type: Type of asset ("crypto", "gold", "forex", "general")
        symbol: Symbol identifier
    """
    await websocket.accept()
    logger.info(f"[WS] New {asset_type} connection for {symbol} (channel: {channel_key})")
    
    # Initialize connection list if not exists
    if channel_key not in active_connections:
        active_connections[channel_key] = []
    
    active_connections[channel_key].append(websocket)
    logger.info(f"[WS] Active connections for {channel_key}: {len(active_connections[channel_key])}")
    
    try:
        while True:
            # Keep connection alive and handle any client messages
            message = await websocket.receive_text()
            logger.debug(f"[WS] Received message from {channel_key}: {message}")
            
            # Optionally handle client messages here
            # For example, client could send subscription preferences
            try:
                client_data = json.loads(message)
                if client_data.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                # Ignore invalid JSON
                pass
            
    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected from {channel_key}")
        
    except Exception as e:
        logger.error(f"[WS] Error in websocket handler for {channel_key}: {e}")
        
    finally:
        # Clean up connection
        if websocket in active_connections.get(channel_key, []):
            active_connections[channel_key].remove(websocket)
            
        # Remove empty channel
        if channel_key in active_connections and not active_connections[channel_key]:
            del active_connections[channel_key]
            logger.info(f"[WS] Removed empty channel: {channel_key}")

async def broadcast_to_clients(symbol, payload, asset_type="crypto"):
    """
    Broadcast data to clients based on symbol and asset type
    
    Args:
        symbol: Symbol to broadcast to (e.g., "BTC-USD", "GOLD", "USD")
        payload: Data to send
        asset_type: Type of asset ("crypto", "gold", "forex")
    """
    # Determine possible channel keys based on asset type
    possible_channels = []
    
    if asset_type == "crypto":
        possible_channels = [
            f"crypto:{symbol}",
            f"crypto:{symbol.upper()}",
            f"crypto:{symbol.lower()}"
        ]
    elif asset_type == "gold":
        possible_channels = ["gold"]
    elif asset_type == "forex":
        possible_channels = [
            f"forex:{symbol}",
            f"forex:{symbol.upper()}",
            symbol.upper()  # for /ws/{symbol} endpoint
        ]
    else:
        # General case
        possible_channels = [symbol, symbol.upper(), symbol.lower()]
    
    logger.info(f"[WS] Broadcasting {asset_type} data for {symbol}")
    logger.info(f"[WS] Checking channels: {possible_channels}")
    logger.info(f"[WS] Available channels: {list(active_connections.keys())}")
    
    total_sent = 0
    
    for channel_key in possible_channels:
        connections = active_connections.get(channel_key, [])
        if connections:
            logger.info(f"[WS] Found {len(connections)} connections for {channel_key}")
            
            # Send to all connections in this channel
            connections_copy = connections.copy()
            for ws in connections_copy:
                try:
                    # Add metadata to payload
                    enhanced_payload = {
                        **payload,
                        "asset_type": asset_type,
                        "channel": channel_key,
                        "timestamp": payload.get("timestamp", "")
                    }
                    
                    await ws.send_text(json.dumps(enhanced_payload))
                    total_sent += 1
                    logger.debug(f"[WS] Sent to {channel_key}")
                    
                except Exception as e:
                    logger.error(f"[WS] Failed to send to {channel_key}: {e}")
                    # Remove broken connection
                    if ws in active_connections.get(channel_key, []):
                        active_connections[channel_key].remove(ws)
    
    if total_sent == 0:
        logger.warning(f"[WS] No connections found for {asset_type}:{symbol}")
    else:
        logger.info(f"[WS] Successfully sent to {total_sent} connections")

# Specific broadcast functions for different asset types
async def broadcast_crypto_price(symbol, payload):
    """Broadcast crypto price update"""
    await broadcast_to_clients(symbol, payload, "crypto")

async def broadcast_gold_price(payload):
    """Broadcast gold price update"""
    await broadcast_to_clients("GOLD", payload, "gold")

async def broadcast_forex_rate(symbol, payload):
    """Broadcast forex rate update"""
    await broadcast_to_clients(symbol, payload, "forex")