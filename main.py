import json
from fastapi import FastAPI, Security, HTTPException, Depends, APIKeyHeader
from pydantic import BaseModel, Field
from datetime import date
import os

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def get_valid_api_keys() -> dict:
    try:
        with open("api_keys.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key header missing",
        )
    valid_keys = get_valid_api_keys()
    key_info = valid_keys.get(api_key_header)
    if key_info and key_info.get("status") == "active":
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or inactive API key",
        )


app = FastAPI(
    title="Numerology API",
    description="A service that generates numerology reports based on name and birth date.",
    version="1.0.0"
)

#Request body model
class NumerologyRequest(BaseModel):
    full_name: str = Field(..., example="Melih Boyacı", title="Full Name", description="The full name of the person for numerology analysis.")
    birth_date: date = Field(..., example="2003-11-26", title="Birth Date", description="The birth date of the person (in YYYY-MM-DD format).")

# Response item model
class ReportItem(BaseModel):
    number: int
    interpretation: str

# Numerology report model
class NumerologyReport(BaseModel):
    life_path_number: ReportItem
    name_number: ReportItem

# Full response model
class NumerologyResponse(BaseModel):
    request_data: NumerologyRequest
    numerology_report: NumerologyReport


PYTHAGOREAN_MAP = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
}

NUMBER_INTERPRETATIONS = {
    1: "Leadership, independence, and pioneering. Represents new beginnings and individuality.",
    2: "Harmony, balance, cooperation, and diplomacy. Symbolizes sensitivity in relationships and partnerships.",
    3: "Creativity, communication, and self-expression. A joyful, social, and artistic energy.",
    4: "Stability, order, discipline, and hard work. The number of reliability and solid foundations.",
    5: "Change, freedom, adventure, and versatility. Embraces the mobility that life brings.",
    6: "Responsibility, family, love, and service. Represents strong ties to community and home.",
    7: "Analysis, inner wisdom, and spirituality. Indicates a researcher with deep thinking and intuition.",
    8: "Power, success, materialism, and authority. Symbolizes competence in financial and worldly matters.",
    9: "Humanism, compassion, completion, and universality. Represents the desire to serve humanity.",
    11: "High intuition, idealism, and enlightenment. Carries the potential of a spiritual guide."
}

"""Reduces a number to a single digit or master number (11, 22, 33)."""
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

@app.post("/numerology", response_model=NumerologyResponse, tags=["Numerology"])
async def create_numerology_report(request: NumerologyRequest):
    
    life_path_num = calculate_life_path(request.birth_date)
    name_num = calculate_name_number(request.full_name)

    report = NumerologyResponse(
        request_data=request,
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
