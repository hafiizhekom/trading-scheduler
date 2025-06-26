# app/router.py
from fastapi import APIRouter, WebSocket, HTTPException, status, Query
from app.websocket_handler import handle_websocket, active_connections
from app.models import PriceOverrideRequest
from app.override_service import handle_override
from app.db import get_crypto_history, get_forex_history, get_gold_history

router = APIRouter()

@router.post("/api/override", status_code=status.HTTP_201_CREATED)
async def override_price(payload: PriceOverrideRequest):
    try:
        await handle_override(payload)
        return {"status": "ok", "message": "Override saved and broadcasted"}
    except Exception as e:
        raise HTTPException(500, detail=f"Override failed: {str(e)}")
    
@router.get("/api/history/crypto/{symbol}")
def api_crypto_history(symbol: str):
    return get_crypto_history(symbol)

@router.get("/api/history/forex/{symbol}")
def api_forex_history(symbol: str):
    return get_forex_history(symbol)

@router.get("/api/history/gold")
def api_gold_history(type_gold: str = Query("ANTAM")):
    return get_gold_history(type_gold)

# Crypto WebSocket endpoint
@router.websocket("/ws/crypto/{symbol}")
async def crypto_websocket_endpoint(websocket: WebSocket, symbol: str):
    """
    WebSocket endpoint for crypto prices
    Example: ws://localhost:8000/ws/crypto/BTC-USD
    """
    channel_key = f"crypto:{symbol}"
    await handle_websocket(websocket, channel_key, "crypto", symbol)

# Gold WebSocket endpoint  
@router.websocket("/ws/gold")
async def gold_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for gold prices
    Example: ws://localhost:8000/ws/gold
    """
    channel_key = "gold"
    await handle_websocket(websocket, channel_key, "gold", "GOLD")

# Forex WebSocket endpoint
@router.websocket("/ws/forex/{symbol}")
async def forex_websocket_endpoint(websocket: WebSocket, symbol: str):
    """
    WebSocket endpoint for forex rates
    Example: ws://localhost:8000/ws/forex/USD
    """
    channel_key = f"forex:{symbol}"
    await handle_websocket(websocket, channel_key, "forex", symbol)

# # Alternative forex endpoint (shorter URL)
# @router.websocket("/ws/{symbol}")
# async def currency_websocket_endpoint(websocket: WebSocket, symbol: str):
#     """
#     Alternative WebSocket endpoint for forex rates
#     Example: ws://localhost:8000/ws/USD
#     """
#     # Assume it's forex if it's 3 characters (currency code)
#     if len(symbol) == 3 and symbol.isupper():
#         channel_key = f"forex:{symbol}"
#         await handle_websocket(websocket, channel_key, "forex", symbol)
#     else:
#         # Fallback to general symbol handling
#         await handle_websocket(websocket, symbol, "general", symbol)

# Debug endpoint
@router.get("/debug/connections")
async def debug_connections():
    return {
        "active_connections": {k: len(v) for k, v in active_connections.items()},
        "total_connections": sum(len(v) for v in active_connections.values()),
        "connection_details": {k: [f"conn_{i}" for i in range(len(v))] for k, v in active_connections.items()}
    }

__all__ = ["router"]