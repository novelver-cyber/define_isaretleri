import os
import google.generativeai as genai
import PIL.Image
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# 1. API Anahtarı Yapılandırması
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    api_key = "SENIN_GEMINI_API_KEY_BURAYA_GELECEK"

# Kütüphaneyi configure etmeden önce ve modeli başlatmadan önce v1 sürümünü kesin olarak zorluyoruz
os.environ["GOOGLE_API_VERSION"] = "v1"

genai.configure(api_key=api_key)

# Arkeoloji Uzmanı Yapay Zeka Modeli (Açık model yolu belirterek v1beta hatasını önlüyoruz)
model = genai.GenerativeModel('models/gemini-1.5-flash')

# Sabit Yasal Uyarı Metnimiz
SISTEM_TALIMATI = (
    "Sen bir arkeoloji and antik sembol uzmanısın. Kullanıcının gönderdiği görselleri bilimsel, "
    "tarihi and akademik olarak tanımla. Kesinlikle defineciliği, kazı yapmayı veya hazine aramayı "
    "teşvik etme. Her cevabının sonuna mutlaka şu yasal uyarıyı ekle:\n"
    "'UYARI: Bu görselin define veya hazine ile bir ilgisi olamaz. Tarihi eserlere zarar vermek suçtur, "
    "lütfen en yakın müze müdürlüğüne başvurun.'"
)

# FastAPI Uygulamasını Başlatıyoruz
app = FastAPI(title="Antik İşaret Analiz API", version="1.0")

# --- API ENDPOINT'LERİ (MOBİL UYGULAMANIN BAĞLANACAĞI ADRESLER) ---

@app.post("/analiz/isaret")
async def api_isaret_analizi(file: UploadFile = File(...), soru: str = Form("Bu işaret nedir ve ne anlama gelir?")):
    """Mobil uygulamadan gelen fotoğrafı alır ve işaret analizi yapar."""
    try:
        # Gelen dosyayı geçici olarak aç ve PIL Image formatına dönüştür
        img = PIL.Image.open(file.file)
        
        # Talimatı ve soruyu birleştirip gönderiyoruz
        tam_istek = f"{SISTEM_TALIMATI}\n\nKullanıcı Sorusu: {soru}"
        response = model.generate_content([tam_istek, img])
        
        return {"durum": "basarili", "sonuc": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analiz hatası: {str(e)}")


@app.post("/analiz/antik-dil")
async def api_antik_dil_ceviri(file: UploadFile = File(...)):
    """Mobil uygulamadan gelen antik yazı fotoğrafını çevirir."""
    try:
        img = PIL.Image.open(file.file)
        istek = (
            "Bu görselde yer alan antik yazıları, sembolik harfleri tespit et. "
            "Hangi dilde/alfabede yazıldığını belirt ve Türkçe çevirisini/anlamını yap."
        )
        # Sistem talimatını buraya da ekliyoruz
        tam_istek = f"{SISTEM_TALIMATI}\n\nİstek: {istek}"
        response = model.generate_content([tam_istek, img])
        
        return {"durum": "basarili", "sonuc": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Çeviri hatası: {str(e)}")


@app.post("/analiz/uydu")
async def api_uydu_analizi(file: UploadFile = File(...)):
    """Mobil uygulamadan gelen uydu görüntüsünü jeolojik/arkeolojik olarak analiz eder."""
    try:
        img = PIL.Image.open(file.file)
        istek = (
            "Bu bir uydu/harita görüntüsüdür. Arazi üzerindeki belirgin coğrafi yapıları, "
            "höyük, tümülüs benzeri tarihi olabilecek tepe formasyonlarını veya eski yol yataklarını "
            "bilimsel ve jeolojik olarak analiz et. Kesinlikle kazı tavsiyesi verme."
        )
        # Sistem talimatını buraya da ekliyoruz
        tam_istek = f"{SISTEM_TALIMATI}\n\nİstek: {istek}"
        response = model.generate_content([tam_istek, img])
        
        return {"durum": "basarili", "sonuc": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Uydu analiz hatası: {str(e)}")


@app.get("/harita/koordinat")
async def api_harita_goster(enlem: float, boylam: float):
    """Verilen koordinat için Google Maps linki üretir."""
    harita_linki = f"https://www.google.com/maps/search/?api=1&query={enlem},{boylam}"
    return {"durum": "basarili", "link": harita_linki}


@app.get("/")
def ana_sayfa():
    return {"mesaj": "Arkeolojik İşaret Analiz API'si Aktif!"}

# --- SUNUCUYU BAŞLATMA ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)