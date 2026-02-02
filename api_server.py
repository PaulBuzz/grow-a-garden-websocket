from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from datetime import datetime

app = FastAPI()

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
    "timestamp": None
}

@app.get("/")
async def root():
    return {"status": "online", "message": "Grow a Garden API"}

@app.get("/stock")
async def get_stock():
    return latest_stock

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Background task to listen to WebSocket
async def websocket_listener():
    import websockets
    
    ws_url = "wss://grown.gleeze.com:2083/"
    
    while True:
        try:
            async with websockets.connect(ws_url) as websocket:
                print("✅ Connected to WebSocket")
                
                async for message in websocket:
                    data = json.loads(message)
                    
                    # Update latest stock
                    latest_stock.update({
                        "seedsStock": data.get("seedsStock", []),
                        "gearStock": data.get("gearStock", []),
                        "eggStock": data.get("eggStock", []),
                        "cosmeticsStock": data.get("cosmeticsStock", []),
                        "eventStock": data.get("eventStock", []),
                        "merchantsStock": data.get("merchantsStock", []),
                        "weather": data.get("weather"),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    print(f"📦 Stock updated: {len(data.get('seedsStock', []))} seeds")
                    
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
            await asyncio.sleep(5)  # Retry after 5 seconds

@app.on_event("startup")
async def startup_event():
    # Start WebSocket listener in background
    asyncio.create_task(websocket_listener())
    print("🚀 API Server started with WebSocket listener")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
