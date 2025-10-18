# server_convert.py
from flask import Flask, request, jsonify
import os
import tempfile
import numpy as np
import librosa
from mido import MidiFile, MidiTrack, Message
import v2m

app = Flask(__name__)


MIDI_DIR = r"midi"

def get_next_midi_path(midi_dir=MIDI_DIR, prefix="output", ext=".mid"):
    """Retourne le chemin du prochain fichier MIDI avec index incrémenté"""
    os.makedirs(midi_dir, exist_ok=True)
    existing = [f for f in os.listdir(midi_dir) if f.startswith(prefix) and f.endswith(ext)]
    indices = []
    for f in existing:
        try:
            # extraire l'entier après le prefix
            idx = int(f[len(prefix):-len(ext)])
            indices.append(idx)
        except ValueError:
            pass
    next_idx = max(indices, default=0) + 1
    return os.path.join(midi_dir, f"{prefix}{next_idx}{ext}")

@app.route("/convert", methods=["POST"])
def convert_wav_to_midi():
    # Vérifie si le fichier est présent
    if "file" not in request.files:
        return jsonify({"error": "no file part (form field 'file' missing)"}), 400

    # Récupère le fichier
    f = request.files["audio"]


    # Récupère les paramètres textuels (bpm, instrument, etc.)
    bpm = request.form.get("bpm", type=float, default=120)
    instrument = request.form.get("instrument", default="piano")
    nb_mesures = request.form.get("nb_mesures", type=int, default=4)
    if f.filename == "":
        return jsonify({"error": "empty filename"}), 400

    # Enregistrer le WAV dans un dossier temporaire
    wav_path = os.path.join(r"recordings", f.filename)  # ou un dossier temp
    f.save(wav_path)

    # Générer le chemin MIDI automatiquement
    midi_path = get_next_midi_path()

    # Convertir WAV → MIDI
    v2m.convert_wav_to_midi(wav_path, midi_path,bpm,nb_mesures)

    return jsonify({"message": f"MIDI enregistre: {midi_path}"})


        

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9004, debug=True)

