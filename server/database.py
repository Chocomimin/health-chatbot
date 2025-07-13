from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"  # Update if using Atlas
client = AsyncIOMotorClient(MONGO_URI)
db = client.chatdb
chats_collection = db.chats
users_collection = db.users  