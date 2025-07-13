import jwt
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import bcrypt
from models import UserCreate, UserLogin
from database import users_collection
from bson import ObjectId
from datetime import datetime, timedelta

router = APIRouter()
SECRET_KEY = "your-secret-key"  # Use env var in production
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ------------------ JWT UTILS ------------------

def create_jwt(user_id: str):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user_id = decode_jwt(token)
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": str(user["_id"]), "username": user["username"]}

# ------------------ AUTH ROUTES ------------------

@router.post("/signup")
async def signup(data: UserCreate):
    existing_user = await users_collection.find_one({"username": data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pw = bcrypt.hash(data.password)
    result = await users_collection.insert_one({
        "username": data.username,
        "password": hashed_pw
    })
    return {"token": create_jwt(str(result.inserted_id))}

@router.post("/login")
async def login(data: UserLogin):
    user = await users_collection.find_one({"username": data.username})
    if not user or not bcrypt.verify(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": create_jwt(str(user["_id"]))}

@router.get("/logout")
async def logout():
    # Just a placeholder — real logout happens on frontend (remove token)
    return {"message": "Logged out. Please discard token on the client."}

@router.get("/me")
async def get_user_info(current_user: dict = Depends(get_current_user)):
    return current_user
