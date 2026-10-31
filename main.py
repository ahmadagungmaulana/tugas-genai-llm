import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = FastAPI(
    title="GenAI Text Analyzer API",
    description="API untuk menganalisis materi pembelajaran berbasis Gemini API"
)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY tidak ditemukan di file .env")

client = genai.Client(api_key=api_key)


class AnalyzeRequest(BaseModel):
    text: str = Field(
        ..., 
        min_length=20, 
        description="Teks materi pembelajaran (minimal 20 karakter)"
    )
    target_audience: str = Field(default="User", description="Target audiens")


# 2. Response Schema (Structured Output)
class AnalyzeResponse(BaseModel):
    summary: str = Field(description="Rangkuman ringkas materi")
    key_points: list[str] = Field(description="Daftar poin-poin utama materi")
    quiz: list[str] = Field(description="Daftar pertanyaan kuis evaluasi")


@app.get("/")
def home():
    return {"message": "GenAI API is running"}


# 3. Endpoint POST utama
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    system_instruction = (
        "Anda adalah Asisten Edukasi AI yang ahli dalam menganalisis "
        "dan menyederhanakan materi pembelajaran."
    )

    prompt = f"""
    [TASK]
    Buatlah bahan belajar terstruktur dari materi yang diberikan.

    [CONTEXT]
    Target Audiens: {request.target_audience}
    Materi Input:
    "{request.text}"

    [CONSTRAINT]
    1. Rangkuman dibuat singkat dan jelas (maksimal 2 kalimat).
    2. Ekstrak poin-poin utama maksimal 5 poin.
    3. HANYA gunakan informasi yang secara eksplisit ada pada teks input. DILARANG MENAMBAHKAN ATAU MENGARANG FAKTA LUAR DI LUAR TEKS INPUT.
    4. Buat tepat 3 pertanyaan kuis evaluasi yang jawabannya terdapat di dalam teks input.
    5. Gunakan bahasa yang ramah dan edukatif.

    [OUTPUT FORMAT]
    Hasil harus mengembalikan format JSON yang sesuai dengan skema output.
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=AnalyzeResponse,
                temperature=0.2, 
            ),
        )

        parsed_result = json.loads(response.text)
        return parsed_result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Terjadi kesalahan saat memproses permintaan AI: {str(e)}"
        )