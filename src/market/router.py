from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
import asyncio
import random
import logging
from src.core.database import AsyncSessionLocal
from src.stocks.models import Stock

router = APIRouter(tags=["Market WebSocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.is_broadcasting = False

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logging.info(f"Client connected. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logging.info(f"Client disconnected. Total active: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logging.warning(f"Failed to send to a client. Removing connection. Error: {str(e)}")
                self.disconnect(connection)

manager = ConnectionManager()

async def live_price_simulator():
    while True:
        if manager.active_connections:
            try:
                async with AsyncSessionLocal() as db:
                    result = await db.execute(select(Stock).where(Stock.is_active == True))
                    stocks = result.scalars().all()

                    if stocks:
                        market_data = {}
                        
                        for stock in stocks:
                            volatility = random.uniform(-0.005, 0.005)
                            new_price = round(stock.current_price * (1 + volatility), 2)
                        
                            stock.current_price = max(0.01, new_price)
                            
                            market_data[stock.symbol] = stock.current_price

                        await db.commit()
                        await manager.broadcast(market_data)

            except Exception as e:
                logging.error(f"Error in broadcast loop: {str(e)}")
        
        await asyncio.sleep(1)

@router.websocket("/ws/market-feed")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    if not manager.is_broadcasting:
        manager.is_broadcasting = True
        asyncio.create_task(live_price_simulator())

    try:
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"Unexpected WebSocket error: {str(e)}")
        manager.disconnect(websocket)