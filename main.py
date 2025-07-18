import json
from fastapi import FastAPI, Security, HTTPException, Depends, Request # Import Request
from fastapi.security import APIKeyHeader
from fastapi import status
from pydantic import BaseModel, Field
from datetime import date
import os

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# ... (the rest of your existing code remains the same up to the endpoint)

app = FastAPI(
    title="Numerology API",
    description="A service that generates numerology reports based on name and birth date.",
    version="1.0.0"
)

# slowapi middleware
app.state.limiter = limiter
# limit aşıldığında çağrılacak handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ... (Pydantic models and helper functions remain the same)
class NumerologyRequest(BaseModel):
    full_name: str = Field(..., example="Melih Boyacı", title="Full Name", description="The full name of the person for numerology analysis.")
    birth_date: date = Field(..., example="2003-11-26", title="Birth Date", description="The birth date of the person (in YYYY-MM-DD format).")

class ReportItem(BaseModel):
    number: int
    interpretation: str

class NumerologyReport(BaseModel):
    life_path_number: ReportItem
    name_number: ReportItem

class NumerologyResponse(BaseModel):
    request_data: NumerologyRequest
    numerology_report: NumerologyReport


PYTHAGOREAN_MAP = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
}

NUMBER_INTERPRETATIONS = {
    1: "Liderlik, bağımsızlık ve öncülük. Yeni başlangıçları ve bireyselliği temsil eder.",
    2: "Uyum, denge, iş birliği ve diplomasi. İlişkilerde ve ortaklıklarda hassasiyeti simgeler.",
    3: "Yaratıcılık, iletişim ve kendini ifade etme. Neşeli, sosyal ve sanatsal bir enerjidir.",
    4: "İstikrar, düzen, disiplin ve sıkı çalışma. Güvenilirliğin ve sağlam temellerin sayısıdır.",
    5: "Değişim, özgürlük, macera ve çok yönlülük. Hayatın getirdiği hareketliliği kucaklar.",
    6: "Sorumluluk, aile, sevgi ve hizmet. Topluluk ve ev ile güçlü bağları temsil eder.",
    7: "Analiz, içsel bilgelik ve maneviyat. Araştırmacı, derin düşünen ve sezgisel bir yapıya işaret eder.",
    8: "Güç, başarı, materyalizm ve otorite. Finansal ve dünyevi konularda yetkinliği simgeler.",
    9: "Hümanizm, şefkat, tamamlanma ve evrensellik. İnsanlığa hizmet etme arzusunu temsil eder.",
    11: "Yüksek sezgi, idealizm ve aydınlanma. Manevi bir yol gösterici potansiyeli taşır.",
    22: "Usta inşaatçı, büyük projeler ve pratik idealizm. Hayalleri gerçeğe dönüştürme gücüdür.",
    33: "Usta öğretici, şifa ve evrensel sevgi. Koşulsuz sevgi ve fedakarlık enerjisidir."
}

def reduce_number(n: int) -> int:
    while n > 9 and n not in [11, 22, 33]:
        n = sum(int(digit) for digit in str(n))
    return n


def calculate_life_path(birth_date: date) -> int:
    total = sum(int(digit) for digit in birth_date.strftime('%Y%m%d'))
    return reduce_number(total)

def calculate_name_number(name: str) -> int:
    name = name.upper().replace('Ç', 'C').replace('Ğ', 'G').replace('İ', 'I').replace('Ö', 'O').replace('Ş', 'S').replace('Ü', 'U')
    total = sum(PYTHAGOREAN_MAP.get(char, 0) for char in name if char.isalpha())
    return reduce_number(total)


@app.post("/numerology",
            response_model=NumerologyResponse,
            tags=["Numerology"]
)
@limiter.limit("10/minute")
# Rename 'request' to 'numerology_request' and add 'request: Request'
async def create_numerology_report(numerology_request: NumerologyRequest, request: Request):

    # Use the new variable name to access the request body
    life_path_num = calculate_life_path(numerology_request.birth_date)
    name_num = calculate_name_number(numerology_request.full_name)

    report = NumerologyResponse(
        # Use the new variable name here as well
        request_data=numerology_request,
        numerology_report=NumerologyReport(
            life_path_number=ReportItem(
                number=life_path_num,
                interpretation=NUMBER_INTERPRETATIONS.get(life_path_num, "No interpretation available.")
            ),
            name_number=ReportItem(
                number=name_num,
                interpretation=NUMBER_INTERPRETATIONS.get(name_num, "No interpretation available.")
            )
        )
    )
    return report