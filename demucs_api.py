import os
import shutil
import uuid
import subprocess

from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Optional: .env Datei laden
load_dotenv()

app = FastAPI()

# API-Key aus Umgebungsvariable oder Fallback
API_KEY = os.getenv("DEMUC_API_KEY", "mein-geheimer-api-key")
OUTPUT_DIR = "separated"

@app.post("/separate")
async def separate_audio(
    file: UploadFile = File(...),
    x_api_key: str = Header(None)
):
    # API Key prüfen
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Ungültiger API Key")

    # Temporären Ordner für Upload anlegen
    temp_id = str(uuid.uuid4())
    temp_dir = os.path.join("temp", temp_id)
    os.makedirs(temp_dir, exist_ok=True)
    input_path = os.path.join(temp_dir, file.filename)

    # Datei speichern
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Demucs ausführen
    try:
        subprocess.run(["demucs", "-o", OUTPUT_DIR, input_path], check=True)
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Demucs Verarbeitung fehlgeschlagen")

    # Output-Pfad finden
    song_name = os.path.splitext(file.filename)[0]
    output_song_dir = os.path.join(OUTPUT_DIR, "htdemucs", song_name)

    if not os.path.exists(output_song_dir):
        raise HTTPException(status_code=500, detail="Getrennte Dateien nicht gefunden")

    # ZIP erstellen
    zip_path = os.path.join(temp_dir, f"{song_name}_stems.zip")
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', output_song_dir)

    # Ergebnis zurückgeben
    return FileResponse(zip_path, media_type='application/zip', filename=f"{song_name}_stems.zip")
