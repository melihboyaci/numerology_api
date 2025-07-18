# numerology-api/Dockerfile

# Python 3.11'in hafif bir versiyonunu temel al
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Önce bağımlılıkları kopyala ve kur. Bu, katman önbellekleme (layer caching) için daha verimlidir.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projenin geri kalan dosyalarını kopyala
COPY . .

# Docker konteyneri dışından erişim için 0.0.0.0 host'u ŞARTTIR!
# 8000 portu konteynerin iç portudur, dışarıyla bir ilgisi yoktur.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]