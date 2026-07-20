import os
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from PIL import Image
import io

app = FastAPI(title="Antik İşaret Analiz API")

# Pydantic Modeli - Çıktının Taş Gibi JSON Gelmesini Garanti Eder
class AnalizResult(BaseModel):
    isaret_adi: str = Field(description="Tespit edilen antik veya define işaretinin adı.")
    donem: str = Field(description="Tahmini tarihi dönem veya medeniyet.")
    kulturel_anlam: str = Field(description="İşaretin derin arkeolojik ve kültürel anlamı.")
    olasi_koordinat_ipuclari: str = Field(description="İşarette bulunan yön, geometri veya mesafe belirten ipuçları.")
    guven_skoru: float = Field(description="0.0 ile 1.0 arasında doğruluk güven skoru.")

# Gemini İstemcisini Başlat (Render'daki GEMINI_API_KEY Çevre Değişkenini Okur)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY çevre değişkeni bulunamadı! Lütfen Render paneline ekleyin.")

client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
Sen antik işaretler, tarihi semboller ve define işaretleri konusunda uzman kıdemli bir arkeologsun.
Sana gönderilen resimdeki işaretleri dikkatlice analiz etmeli ve sadece belirtilen şemaya uygun bir JSON çıktısı vermelisin.

Özellikle şu işaretler konusunda uzmansın:
Ayak İzi, Haç, Güneş, Göz, Yılan, Niş, Kaplumbağa, Tavuk ve Civcivler, Balık, Merdiven, Ok İşareti, Nal, El, Zincir, Üçgen, Yuvarlak Oyma, Kare Oyma, Koltuk Taşı, Deve, Aslan, Kılıç, Terazi, Çapa, Akrep, Baklava Dilimi, Halka, Boynuz, Hilal, Tabanca/Tüfek, Güvercin, Mahzen İşareti.
"""

@app.post("/analiz/uydu", response_model=AnalizResult)
async def api_uydu_analizi(file: UploadFile = File(...)):
    # Dosya tipi kontrolü
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Lütfen geçerli bir resim dosyası yükleyin (JPEG, PNG vb.).")
    
    try:
        # Resmi oku ve PIL formatına çevir
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Gemini 2.0 Flash modelini çağır
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[image, "Bu resimdeki antik/define işaretini sistem talimatlarına göre analiz et."],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=AnalizResult,
            ),
        )
        
        # Gelen yanıtı JSON olarak parse et ve modele dök
        result_data = json.loads(response.text)
        return AnalizResult(**result_data)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Gemini API çıktısı geçerli bir JSON formatında üretilemedi.")
    except genai.errors.APIError as e:
        if "RESOURCE_EXHAUSTED" in str(e):
            raise HTTPException(status_code=429, detail="Gemini API Kotası Aşılı veya Limit Sıfırlandı. Lütfen yeni bir hesap/anahtar deneyin.")
        raise HTTPException(status_code=500, detail=f"Google Gemini API Hatası: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sunucu hatası: {str(e)}")a