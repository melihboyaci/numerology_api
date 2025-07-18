# numerology-api/Dockerfile

# Python 3.11'in hafif bir versiyonunu temel al
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Sistem bağımlılıklarını kur
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Önce bağımlılıkları kopyala ve kur. Bu, katman önbellekleme (layer caching) için daha verimlidir.
COPY requirements.txt .

# Python bağımlılıklarını kur
RUN pip install --no-cache-dir -r requirements.txt

# Projenin geri kalan dosyalarını kopyala
COPY . .

# api_keys.json dosyası yoksa oluştur
RUN if [ ! -f api_keys.json ]; then echo '{}' > api_keys.json; fi

# Portu aç
EXPOSE 8000

# Sağlık kontrolü
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Docker konteyneri dışından erişim için 0.0.0.0 host'u ŞARTTIR!
# 8000 portu konteynerin iç portudur, dışarıyla bir ilgisi yoktur.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]