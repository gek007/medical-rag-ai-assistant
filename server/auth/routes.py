from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from config.db import users_collection
from config.limiter import limiter
from config.logger import get_logger

from .hash_utils import hash_password, verify_password
from .models import SignupRequest

logger = get_logger("auth.routes")
logger.info("auth.routes module initialized")

router = APIRouter()
security = HTTPBasic()


def authenticate(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    logger.info("Authentication attempt | username=%s", credentials.username)
    user = users_collection.find_one({"username": credentials.username})

    if not user:
        logger.warning("Authentication failed — user not found | username=%s", credentials.username)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(credentials.password, user["password"]):
        logger.warning("Authentication failed — wrong password | username=%s", credentials.username)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    logger.info("Authentication successful | username=%s role=%s", credentials.username, user["role"])
    return user


@router.post("/signup")
@limiter.limit("5/minute")
def signup(request: Request, body: SignupRequest):
    logger.info("Signup attempt | username=%s role=%s", body.username, body.role)

    if body.role == "admin":
        logger.warning("Signup rejected — admin role self-assignment attempt | username=%s", body.username)
        raise HTTPException(status_code=403, detail="Cannot self-assign admin role")

    if users_collection.find_one({"username": body.username}):
        logger.warning("Signup failed — username already exists | username=%s", body.username)
        raise HTTPException(status_code=400, detail="Username already exists")

    users_collection.insert_one(
        {
            "username": body.username,
            "password": hash_password(body.password),
            "role": body.role,
        }
    )
    logger.info("User created successfully | username=%s role=%s", body.username, body.role)
    return {"message": "User created successfully"}


@router.get("/login")
@limiter.limit("10/minute")
def login(request: Request, user=Depends(authenticate)):
    logger.info("Login successful | username=%s role=%s", user["username"], user["role"])
    return {
        "message": f"Logged in successfully as {user['username']}",
        "role": user["role"],
    }
