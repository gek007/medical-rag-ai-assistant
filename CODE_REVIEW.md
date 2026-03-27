# Code Review: Medical RAG AI Assistant

**Date:** 2026-03-27

---

## Architecture

- FastAPI + MongoDB Atlas + Pinecone vector store
- HTTP Basic Auth + bcrypt
- Role-based access (admin/doctor) for PDF upload/processing

---

## Critical Issues

**1. No file type or size validation** (`server/docs/routes.py`, `server/docs/vectorstore.py`)
Any file type is accepted; files are read entirely into memory. Adds DOS risk and will crash `PyPDFLoader` on non-PDFs.

**2. Uploaded files never deleted** (`server/docs/vectorstore.py:81-86`)
PDFs are saved to `uploaded_docs/` and never cleaned up after vectorization. This is a serious concern for a medical app — sensitive documents should not persist on disk.

**3. Unvalidated `role` form field** (`server/docs/routes.py:20`)
The `role` parameter from the upload form is never validated against allowed values and is echoed back in the response. It should be derived from the authenticated user, not the form.

**4. No input validation on signup** (`server/auth/routes.py`)
No length/format constraints on username or password fields. Empty strings are accepted.

---

## High Priority

**5. No rate limiting** — `main.py` has no middleware to prevent abuse of auth or upload endpoints.

**6. Unhandled DB errors** — MongoDB operations in auth routes have no try/catch. Any connection issue returns a raw 500 with exception details.

**7. No CORS configuration** — Will block browser-based clients.

---

## Medium Priority

**8. Blocking PDF loading** (`server/docs/vectorstore.py:94`) — `PyPDFLoader.load()` is synchronous and blocks the event loop.

**9. Upload endpoint not async** (`server/docs/routes.py:16`) — `def upload_docs` should be `async def`.

**10. Function name typo** — `load_vectorestore` → `load_vectorstore`.

**11. Hardcoded magic numbers** — Chunk size (500), overlap (100), batch size (100), log rotation (5MB) should be in config.

---

## Low Priority

- `Optional` imported but unused in `server/auth/models.py`
- `logger.propagate = False` set twice in `server/config/logger.py`
- Console handler level is `DEBUG` but README says `INFO`
- No request ID tracking, making log correlation difficult
- 0% test coverage

---

## Security Summary

| Area | Status |
|------|--------|
| Password hashing | Good (bcrypt) |
| File upload security | Poor (no type/size checks) |
| Input validation | Poor |
| Data retention (PHI) | Concerning (files not deleted) |
| Rate limiting | Missing |
| API auth | Adequate |

---

## Top 3 Actions Before Any Production Use

1. Add file type/size validation + delete temp files after processing
2. Validate and whitelist the `role` parameter; derive from auth context
3. Add Pydantic field validators on signup (`min_length`, `max_length`)
