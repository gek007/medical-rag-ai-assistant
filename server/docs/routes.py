import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from auth import authenticate
from config.db import documents_collection
from config.logger import get_logger

from .vectorstore import load_vectorstore

logger = get_logger("docs.routes")
logger.info("docs.routes module initialized")

router = APIRouter()


@router.post("/upload")
async def upload_docs(
    user=Depends(authenticate),
    file: UploadFile = File(...),
    role: str = Form(...),
):
    role = role.strip()
    valid_roles: tuple[str, ...] = ("doctor", "admin", "user")
    if role not in valid_roles:
        raise HTTPException(status_code=422, detail=f"role must be one of: {', '.join(valid_roles)}")

    logger.info(
        "Upload request | user=%s user_role=%s file=%s target_role=%s",
        user["username"],
        user["role"],
        file.filename,
        role,
    )

    if user["role"] != "admin":
        logger.warning(
            "Upload forbidden — insufficient role | user=%s role=%s",
            user["username"],
            user["role"],
        )
        raise HTTPException(status_code=403, detail="Forbidden")

    doc_id = str(uuid.uuid4())
    logger.info("Processing upload | doc_id=%s file=%s", doc_id, file.filename)

    try:
        await load_vectorstore([file], role, doc_id)
    except Exception as e:
        logger.error(
            "Upload failed | doc_id=%s file=%s error=%s",
            doc_id,
            file.filename,
            e,
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Failed to process document")

    documents_collection.insert_one({
        "doc_id": doc_id,
        "filename": file.filename,
        "role": role,
        "uploaded_by": user["username"],
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    })

    logger.info("Upload complete | doc_id=%s file=%s", doc_id, file.filename)
    return {
        "message": f"File {file.filename} uploaded successfully",
        "doc_id": doc_id,
        "role": role,
    }


@router.get("/documents")
async def list_documents(user=Depends(authenticate)):
    user_role = user["role"]

    if user_role == "admin":
        cursor = documents_collection.find({}, {"_id": 0})
    else:
        cursor = documents_collection.find({"role": user_role}, {"_id": 0})

    docs = list(cursor)
    logger.info(
        "Documents listed | user=%s role=%s count=%d",
        user["username"],
        user_role,
        len(docs),
    )
    return {"documents": docs}
