FROM python:3.10-slim

# Systemabhängigkeiten
RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis setzen
WORKDIR /app

# Projektdateien kopieren
COPY . .

# Abhängigkeiten installieren
RUN pip install --no-cache-dir -r requirements.txt

# Uvicorn-Server starten (ersetze ggf. "demucs_api" mit deinem FastAPI-Dateinamen)
CMD ["uvicorn", "demucs_api:app", "--host", "0.0.0.0", "--port", "8000"]
