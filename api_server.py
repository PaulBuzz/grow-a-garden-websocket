from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Grow A Garden API - Real Data")

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
        "message": "Grow a Garden Real-Time API (REST-based)",
        "data_source": "gagstock.gleeze.com",
        "connected": latest_stock["connected"],
        "last_update": latest_stock["timestamp"]
    }

@app.get("/stock")
async def get_stock():
    return latest_stock

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "connected": latest_stock["connected"],
        "timestamp": datetime.now().isoformat()
    }

# Fetch from REST API
async def fetch_stock_data():
    import aiohttp
    
    api_url = "https://gagstock.gleeze.com/grow-a-garden"
    
    while True:
        try:
            logger.info(f"🔄 Fetching from: {api_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Transform gleeze.com format to our format
                        seed_items = []
                        for item in data.get("seed", {}).get("items", []):
                            seed_items.append({
                                "name": item.get("name", "Unknown"),
                                "stock": item.get("stock", 0),
                                "rarity": item.get("rarity", "Unknown"),
                                "price": item.get("price", 0),
                                "imageUrl": item.get("imageUrl", "")
                            })
                        
                        gear_items = []
                        for item in data.get("gear", {}).get("items", []):
                            gear_items.append({
                                "name": item.get("name", "Unknown"),
                                "stock": item.get("stock", 0),
                                "rarity": item.get("rarity", "Unknown"),
                                "price": item.get("price", 0),
                                "imageUrl": item.get("imageUrl", "")
                            })
                        
                        egg_items = []
                        for item in data.get("egg", {}).get("items", []):
                            egg_items.append({
                                "name": item.get("name", "Unknown"),
                                "stock": item.get("stock", 0),
                                "rarity": item.get("rarity", "Unknown"),
                                "price": item.get("price", 0),
                                "imageUrl": item.get("imageUrl", "")
                            })
                        
                        cosmetic_items = []
                        for item in data.get("cosmetic", {}).get("items", []):
                            cosmetic_items.append({
                                "name": item.get("name", "Unknown"),
                                "stock": item.get("stock", 0),
                                "rarity": item.get("rarity", "Unknown"),
                                "price": item.get("price", 0),
                                "imageUrl": item.get("imageUrl", "")
                            })
                        
                        event_items = []
                        for item in data.get("event", {}).get("items", []):
                            event_items.append({
                                "name": item.get("name", "Unknown"),
                                "stock": item.get("stock", 0),
                                "rarity": item.get("rarity", "Unknown"),
                                "price": item.get("price", 0),
                                "imageUrl": item.get("imageUrl", "")
                            })
                        
                        merchant_items = []
                        for item in data.get("merchant", {}).get("items", []):
                            merchant_items.append({
                                "name": item.get("name", "Unknown"),
                                "stock": item.get("stock", 0),
                                "rarity": item.get("rarity", "Unknown"),
                                "price": item.get("price", 0),
                                "imageUrl": item.get("imageUrl", "")
                            })
                        
                        # Update stock
                        latest_stock.update({
                            "seedsStock": seed_items,
                            "gearStock": gear_items,
                            "eggStock": egg_items,
                            "cosmeticsStock": cosmetic_items,
                            "eventStock": event_items,
                            "merchantsStock": merchant_items,
                            "weather": data.get("weather"),
                            "timestamp": datetime.now().isoformat(),
                            "connected": True
                        })
                        
                        logger.info(f"✅ Stock updated: {len(seed_items)} seeds, {len(gear_items)} gear, {len(egg_items)} eggs")
                        
                    else:
                        logger.error(f"❌ API returned status {response.status}")
                        latest_stock["connected"] = False
                        
        except asyncio.TimeoutError:
            logger.error("❌ Request timeout")
            latest_stock["connected"] = False
            
        except Exception as e:
            logger.error(f"❌ API error: {e}")
            latest_stock["connected"] = False
            
        # Update every 30 seconds
        await asyncio.sleep(30)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting API server with REST data fetcher...")
    asyncio.create_task(fetch_stock_data())
    logger.info("✅ Background data fetcher started (updates every 30s)")

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🌐 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
