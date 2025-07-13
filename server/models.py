from pydantic import BaseModel

class ChatInput(BaseModel):
    message: str
    session_id: str

class ChatOutput(BaseModel):
    reply: str
    emotion: str

class CreateChatModel(BaseModel):
    name: str

class RenameChatModel(BaseModel):
    chat_id: str
    new_name: str

class UpdateMessageModel(BaseModel):
    chat_id: str
    index: int
    new_message: str
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str
