from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import httpx
import cv2
import numpy as np
import pytesseract
import easyocr
import whisper
import os
from app.config import settings
from app.logger import logger

router = APIRouter(prefix="/api")

class QueryRequest(BaseModel):
    prompt: str
    model: str = "llama3"

@router.post("/langchain")
async def langchain_invoke(req: QueryRequest):
    try:
        from langchain_community.llms import Ollama
        llm = Ollama(base_url=settings.ollama_host, model=req.model)
        result = llm.invoke(req.prompt)
        return {"result": result}
    except Exception as e:
        logger.error("LangChain invoke error", e)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.ollama_host}/api/generate",
                    json={"model": req.model, "prompt": req.prompt, "stream": False},
                    timeout=10.0
                )
                if response.status_code == 200:
                    return {"result": response.json().get("response"), "fallback": True}
        except Exception:
            pass
        return {"error": str(e), "message": "Failed to run LangChain. Make sure Ollama has model loaded."}

@router.post("/llamaindex")
async def llamaindex_query(req: QueryRequest):
    try:
        from llama_index.llms.ollama import Ollama
        from llama_index.core import Settings
        
        Settings.llm = Ollama(model=req.model, base_url=settings.ollama_host)
        Settings.embed_model = "local"

        from llama_index.core import Document, VectorStoreIndex
        documents = [Document(text="DevForge is a hardened local developer platform.")]
        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()
        response = query_engine.query(req.prompt)
        
        return {"result": str(response)}
    except Exception as e:
        logger.error("LlamaIndex query error", e)
        return {"error": str(e), "message": "LlamaIndex mock RAG execution failed."}

@router.post("/ocr")
async def perform_ocr(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file.")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        extracted_text_tesseract = ""
        extracted_text_easyocr = ""

        try:
            extracted_text_tesseract = pytesseract.image_to_string(gray)
        except Exception as e:
            logger.warn("Tesseract OCR not fully configured on host", e)
            extracted_text_tesseract = f"Error: {str(e)}"

        try:
            reader = easyocr.Reader(['en'], gpu=False)
            results = reader.readtext(img)
            extracted_text_easyocr = " ".join([res[1] for res in results])
        except Exception as e:
            logger.warn("EasyOCR reader execution error", e)
            extracted_text_easyocr = f"Error: {str(e)}"

        return {
            "tesseract": extracted_text_tesseract.strip(),
            "easyocr": extracted_text_easyocr.strip()
        }
    except Exception as e:
        logger.error("OCR execution error", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/whisper")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        temp_filename = f"temp_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            buffer.write(await file.read())

        transcription = "Whisper transcription not executed"
        try:
            model = whisper.load_model("tiny", device="cpu")
            result = model.transcribe(temp_filename)
            transcription = result.get("text", "")
        except Exception as e:
            logger.warn("Whisper model load/transcribe failed", e)
            transcription = f"Transcription failed: {str(e)}"
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

        return {"transcription": transcription.strip()}
    except Exception as e:
        logger.error("Whisper transcription error", e)
        raise HTTPException(status_code=500, detail=str(e))
