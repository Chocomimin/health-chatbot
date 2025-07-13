# from fastapi import APIRouter
# from bson import ObjectId
# from database import chats_collection
# from models import *
# from utils import detect_emotion_with_embeddings, detect_intent, handle_smalltalk, ask_healthcare_bot

# router = APIRouter()

# @router.post("/chat", response_model=ChatOutput)
# async def chat_endpoint(chat: ChatInput):
#     session_id = chat.session_id
#     user_input = chat.message.strip()

#     chat_doc = await chats_collection.find_one({"_id": ObjectId(session_id)})
#     history = chat_doc["messages"] if chat_doc else []
#     formatted_history = [{"role": m["role"], "message": m["message"]} for m in history]

#     emotion = detect_emotion_with_embeddings(user_input)
#     intent = detect_intent(user_input)

#     if intent in ["greeting", "smalltalk"]:
#         reply = handle_smalltalk(intent, user_input)
#     elif intent in ["healthcare", "unknown"]:
#         reply = ask_healthcare_bot(user_input, formatted_history)
#     else:
#         reply = "🫶 Could you please tell me more about your health concerns?"

#     new_msgs = [
#         {"role": "USER", "message": user_input},
#         {"role": "CHATBOT", "message": reply}
#     ]
#     await chats_collection.update_one(
#         {"_id": ObjectId(session_id)},
#         {"$push": {"messages": {"$each": new_msgs}}}
#     )

#     return ChatOutput(reply=reply, emotion=emotion)

# @router.post("/chat/create")
# async def create_chat(data: CreateChatModel):
#     chat = {"name": data.name, "messages": []}
#     result = await chats_collection.insert_one(chat)
#     return {"chat_id": str(result.inserted_id), "name": data.name}

# @router.get("/chat/sessions")
# async def list_chats():
#     chats = await chats_collection.find().to_list(None)
#     return [{"chat_id": str(c["_id"]), "name": c["name"]} for c in chats]

# @router.delete("/chat/{chat_id}")
# async def delete_chat(chat_id: str):
#     result = await chats_collection.delete_one({"_id": ObjectId(chat_id)})
#     return {"deleted": result.deleted_count > 0}

# @router.put("/chat/rename")
# async def rename_chat(data: RenameChatModel):
#     await chats_collection.update_one({"_id": ObjectId(data.chat_id)}, {"$set": {"name": data.new_name}})
#     return {"message": "Chat renamed"}

# @router.get("/chat/{chat_id}")
# async def get_chat(chat_id: str):
#     chat = await chats_collection.find_one({"_id": ObjectId(chat_id)})
#     if not chat:
#         return {"error": "Chat not found"}
#     return {
#         "chat_id": str(chat["_id"]),
#         "name": chat["name"],
#         "messages": chat["messages"]
#     }

# @router.put("/chat/edit-message")
# async def edit_message(data: UpdateMessageModel):
#     await chats_collection.update_one(
#         {"_id": ObjectId(data.chat_id)},
#         {"$set": {f"messages.{data.index}.message": data.new_message}}
#     )
#     return {"message": "Message updated"}


from fastapi import APIRouter
from bson import ObjectId
from database import chats_collection
from models import *
from utils import detect_emotion_with_embeddings, detect_intent, handle_smalltalk, ask_healthcare_bot
from fastapi import Depends
from auth import get_current_user
router = APIRouter()

@router.post("/chat", response_model=ChatOutput)
async def chat_endpoint(chat: ChatInput):
    session_id = chat.session_id
    user_input = chat.message.strip()

    chat_doc = await chats_collection.find_one({"_id": ObjectId(session_id)})
    history = chat_doc["messages"] if chat_doc else []
    formatted_history = [{"role": m["role"], "message": m["message"]} for m in history]

    emotion = detect_emotion_with_embeddings(user_input)
    intent = detect_intent(user_input)

    if intent in ["greeting", "smalltalk"]:
        reply = handle_smalltalk(intent, user_input)
    elif intent in ["healthcare", "unknown"]:
        reply = ask_healthcare_bot(user_input, formatted_history)
    else:
        reply = "🫶 Could you please tell me more about your health concerns?"

    new_msgs = [
        {"role": "USER", "message": user_input},
        {"role": "CHATBOT", "message": reply}
    ]
    await chats_collection.update_one(
        {"_id": ObjectId(session_id)},
        {"$push": {"messages": {"$each": new_msgs}}}
    )

    return ChatOutput(reply=reply, emotion=emotion)

@router.post("/chat/create")
async def create_chat(data: CreateChatModel, current_user: dict = Depends(get_current_user)):
    chat = {
        "name": data.name,
        "messages": [],
        "user_id": current_user["id"]  # Store user ID
    }
    result = await chats_collection.insert_one(chat)
    return {"chat_id": str(result.inserted_id), "name": data.name}

@router.get("/chat/sessions")
async def list_chats(current_user: dict = Depends(get_current_user)):
    chats = await chats_collection.find({"user_id": current_user["id"]}).to_list(None)
    return [{"chat_id": str(c["_id"]), "name": c["name"]} for c in chats]

@router.delete("/chat/{chat_id}")
async def delete_chat(chat_id: str):
    result = await chats_collection.delete_one({"_id": ObjectId(chat_id)})
    return {"deleted": result.deleted_count > 0}

@router.put("/chat/rename")
async def rename_chat(data: RenameChatModel):
    await chats_collection.update_one({"_id": ObjectId(data.chat_id)}, {"$set": {"name": data.new_name}})
    return {"message": "Chat renamed"}

@router.get("/chat/{chat_id}")
async def get_chat(chat_id: str, current_user: dict = Depends(get_current_user)):
    chat = await chats_collection.find_one({"_id": ObjectId(chat_id), "user_id": current_user["id"]})
    if not chat:
        return {"error": "Chat not found"}
    return {
        "chat_id": str(chat["_id"]),
        "name": chat["name"],
        "messages": chat["messages"]
    }

@router.put("/chat/edit-message")
async def edit_message(data: UpdateMessageModel):
    await chats_collection.update_one(
        {"_id": ObjectId(data.chat_id)},
        {"$set": {f"messages.{data.index}.message": data.new_message}}
    )
    return {"message": "Message updated"}

