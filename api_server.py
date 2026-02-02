from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from datetime import datetime
import logging
import uvicorn
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Grow A Garden API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store latest stock data
latest_stock = {
    "seedsStock": [],
    "gearStock": [],
    "eggStock": [],
    "cosmeticsStock": [],
    "eventStock": [],
    "merchantsStock": [],
    "weather": None,
    "timestamp": None,
    "connected": False
}

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Grow a Garden Real-Time API",
        "websocket_connected": latest_stock["connected"],
        "last_update": latest_stock["timestamp"]
    }

@app.get("/stock")
async def get_stock():
    return latest_stock

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "websocket_connected": latest_stock["connected"],
        "timestamp": datetime.now().isoformat()
    }

# Background WebSocket listener
async def websocket_listener():
    import websockets
    
    DISCORD_USER_ID = "945342822658224209"  # ⬅️ CHANGE THIS!
    ws_url = f"wss://websocket.joshlei.com/growagarden?user_id={DISCORD_USER_ID}"
    
    while True:
        try:
            logger.info(f"🔌 Connecting to WebSocket: {ws_url}")

            async with websockets.connect(ws_url, ping_interval=30, ping_timeout=10) as websocket:
                logger.info("✅ Connected to Grow A Garden WebSocket!")
                latest_stock["connected"] = True
                
                async for message in websocket:
                    try:
                        data = json.loads(message)

                        # Update latest stock from the new format
                        latest_stock.update({
                            "seedsStock": data.get("SEED_STOCK", []),
                            "gearStock": data.get("GEAR_STOCK", []),
                            "eggStock": data.get("EGG_STOCK", []),
                            "cosmeticsStock": data.get("COSMETIC_STOCK", []),
                            "eventStock": data.get("EVENTSHOP_STOCK", []),
                            "merchantsStock": [],  # Not in this API
                            "weather": data.get("WEATHER"),
                            "timestamp": datetime.now().isoformat(),
                            "connected": True
                        })

                        seeds_count = len(data.get("SEED_STOCK", []))
                        logger.info(f"📦 Stock updated: {seeds_count} seeds available")

                    except json.JSONDecodeError as e:
                        logger.error(f"❌ JSON parse error: {e}")
                        continue

        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
            latest_stock["connected"] = False
            await asyncio.sleep(5)  # Wait before reconnecting

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting API server...")
    asyncio.create_task(websocket_listener())
    logger.info("🎧 WebSocket listener started")

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
