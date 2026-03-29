import asyncio
import os
import time
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec

from config.logger import get_logger

load_dotenv()

logger = get_logger("docs.vectorstore")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is not set in environment")
if not PINECONE_API_KEY:
    logger.error("PINECONE_API_KEY is not set in environment")
if not PINECONE_INDEX_NAME:
    logger.error("PINECONE_INDEX_NAME is not set in environment")
if not PINECONE_ENVIRONMENT:
    logger.error("PINECONE_ENVIRONMENT is not set in environment")

UPLOAD_DIR = Path(__file__).parent.parent / "uploaded_docs"
UPLOAD_DIR.mkdir(exist_ok=True)
logger.info("Upload directory ready | path=%s", UPLOAD_DIR)


def get_index():
    logger.info("Connecting to Pinecone | index=%s", PINECONE_INDEX_NAME)
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        existing_indexes = [i["name"] for i in pc.list_indexes()]
        logger.info("Pinecone connected | existing_indexes=%s", existing_indexes)

        if PINECONE_INDEX_NAME not in existing_indexes:
            logger.info(
                "Index not found — creating | index=%s region=%s",
                PINECONE_INDEX_NAME,
                PINECONE_ENVIRONMENT,
            )
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=768,
                metric="dotproduct",
                spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT),
            )
            logger.info(
                "Waiting for index to become ready | index=%s", PINECONE_INDEX_NAME
            )
            while not pc.describe_index(PINECONE_INDEX_NAME).status.ready:
                time.sleep(1)
            logger.info("Index is ready | index=%s", PINECONE_INDEX_NAME)
        else:
            logger.info("Index already exists | index=%s", PINECONE_INDEX_NAME)

        return pc.Index(PINECONE_INDEX_NAME)
    except Exception as e:
        logger.error("Failed to connect to Pinecone | error=%s", e, exc_info=True)
        raise


async def load_vectorstore(
    uploaded_files: list, role: Literal["doctor", "admin", "user"], doc_id: str
) -> None:
    logger.info(
        "Starting vectorstore load | doc_id=%s role=%s files=%d",
        doc_id,
        role,
        len(uploaded_files),
    )

    try:
        index = await asyncio.to_thread(get_index)
    except Exception:
        logger.error(
            "Aborting vectorstore load — could not get Pinecone index | doc_id=%s",
            doc_id,
        )
        raise

    embed_model = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=768)
    logger.info(
        "Embedding model initialized | model=text-embedding-3-small dimensions=768"
    )

    for file in uploaded_files:
        # Use only the basename to prevent path traversal
        safe_filename = Path(file.filename).name
        save_path = UPLOAD_DIR / safe_filename
        logger.info("Saving uploaded file | file=%s path=%s", safe_filename, save_path)

        try:
            contents = await file.read()
            # Validate PDF magic bytes
            if not contents.startswith(b"%PDF"):
                raise ValueError(f"File {safe_filename} is not a valid PDF")
            with open(save_path, "wb") as f:
                f.write(contents)
            logger.info("File saved | file=%s", safe_filename)
        except Exception as e:
            logger.error(
                "Failed to save file | file=%s error=%s",
                safe_filename,
                e,
                exc_info=True,
            )
            raise

        logger.info("Loading PDF | file=%s", safe_filename)
        try:
            loader = PyPDFLoader(str(save_path))
            documents = loader.load()
            logger.info("PDF loaded | file=%s pages=%d", safe_filename, len(documents))
        except Exception as e:
            logger.error(
                "Failed to load PDF | file=%s error=%s", safe_filename, e, exc_info=True
            )
            raise

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=100
        )
        chunks = text_splitter.split_documents(documents)
        logger.info(
            "Text split into chunks | file=%s chunks=%d",
            safe_filename,
            len(chunks),
        )

        texts = [chunk.page_content for chunk in chunks]
        ids = [f"{doc_id}-{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "source": safe_filename,
                "role": role,
                "doc_id": doc_id,
                "page": chunk.metadata.get("page", 0),
                "text": chunk.page_content,
            }
            for chunk in chunks
        ]

        logger.info(
            "Generating embeddings | file=%s chunks=%d",
            safe_filename,
            len(texts),
        )
        try:
            embeddings = await asyncio.to_thread(embed_model.embed_documents, texts)
            logger.info(
                "Embeddings generated | file=%s count=%d",
                safe_filename,
                len(embeddings),
            )
        except Exception as e:
            logger.error(
                "Embedding failed | file=%s error=%s", safe_filename, e, exc_info=True
            )
            raise

        vectors = [
            {"id": vid, "values": values, "metadata": meta}
            for vid, values, meta in zip(ids, embeddings, metadatas)
        ]

        batch_size = 100
        logger.info(
            "Upserting vectors to Pinecone | file=%s vectors=%d batch_size=%d",
            safe_filename,
            len(vectors),
            batch_size,
        )
        try:
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i : i + batch_size]
                await asyncio.to_thread(index.upsert, vectors=batch)
                logger.info(
                    "Batch upserted | file=%s batch=%d-%d",
                    safe_filename,
                    i,
                    i + len(batch),
                )
            logger.info(
                "Vectors upserted | file=%s num_chunks=%d",
                safe_filename,
                len(vectors),
            )
        except Exception as e:
            logger.error(
                "Pinecone upsert failed | file=%s error=%s",
                safe_filename,
                e,
                exc_info=True,
            )
            raise

        logger.info(
            "Vectorstore load complete | doc_id=%s file=%s", doc_id, safe_filename
        )
