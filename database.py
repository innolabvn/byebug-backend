from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from typing import Optional
import os

client: Optional[AsyncIOMotorClient] = None

def get_database() -> AsyncIOMotorClient:
    """Return a MongoDB client instance."""
    global client
    if client is None:
        mongo_uri = os.environ.get("MONGODB_URI", "mongodb://mongo:27017")
        client = AsyncIOMotorClient(mongo_uri)
    return client


