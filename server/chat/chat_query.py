import asyncio
import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone

from config.logger import get_logger

load_dotenv()

logger = get_logger("chat.chat_query")
logger.info("chat.chat_query module initialized")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

embed_model = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=768)
logger.info("Embedding model initialized | model=text-embedding-3-small dimensions=768")

llm = ChatGroq(model="llama3-8b-8192", api_key=os.getenv("GROQ_API_KEY"))
logger.info("LLM model initialized | model=llama3-8b-8192")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful and knowledgeable medical assistant. "
            "Answer questions based on the following documents: {context}",
            "Include the document source in the answer.",
        ),
        ("human", "{question}"),
    ]
)

rag_chain = prompt | llm

logger.info("Chain initialized")


async def answer_question(question: str, user_role: str) -> str:

    try:
        # Embed the user's question as usual
        vectors = await asyncio.to_thread(embed_model.embed_query, question)
        results = await asyncio.to_thread(
            index.query, vectors, top_k=3, include_metadata=True
        )

        filtered_context = []
        sources = set()

        for match in results["matches"]:
            metadata = match["metadata"]
            if metadata.get("role") == user_role:
                filtered_context.append(metadata.get("text", "") + "\\n")
                sources.add(metadata.get("source"))

        if not filtered_context:
            return "No relevant information found for your question."

        docs_text = "\\n".join(filtered_context)

        final_answer = await asyncio.to_thread(
            rag_chain.ainvoke, {"context": docs_text, "question": question}
        )

        return {"answer": final_answer.content, "sources": list(sources)}

    except Exception as e:
        logger.error("Error querying Pinecone | error=%s", e, exc_info=True)
        raise

    finally:
        logger.info("Chat query completed")
