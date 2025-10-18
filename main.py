# server_convert.py
from flask import Flask, request, send_file ,  jsonify
from flask_cors import CORS
import os
import tempfile
import numpy as np
import librosa
from mido import MidiFile, MidiTrack, Message
import v2m
import audio_tools.midi_to_wav , audio_tools.mixer


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

MIDI_DIR = r"midi"

def get_next_midi_path(instrument, midi_dir=MIDI_DIR, ext=".mid"):
    """
    Retourne le chemin du prochain fichier MIDI pour un instrument donné.
    Exemple : piano_1.mid, piano_2.mid, guitare_1.mid, ...
    """
    os.makedirs(midi_dir, exist_ok=True)

    # Lister les fichiers commençant par le nom de l’instrument
    existing = [f for f in os.listdir(midi_dir)
                if f.startswith(f"{instrument}_") and f.endswith(ext)]

    indices = []
    for f in existing:
        try:
            # extraire l'indice après le nom de l’instrument
            idx_str = f[len(instrument) + 1 : -len(ext)]
            idx = int(idx_str)
            indices.append(idx)
        except ValueError:
            pass

    next_idx = max(indices, default=0) + 1
    filename = f"{instrument}_{next_idx}{ext}"
    return os.path.join(midi_dir, filename)



###################


@app.route("/convert", methods=["POST"])
def convert_wav_to_midi():
    # Vérifie si le fichier est présent
    if "audio" not in request.files:
        return jsonify({"error": "no file part (form field 'file' missing)"}), 400

    # Récupère le fichier
    f = request.files["audio"]


    # Récupère les paramètres textuels (bpm, instrument, etc.)
    bpm = request.form.get("bpm", type=float, default=120)
    instrument = request.form.get("instrument", default="piano")
    nb_mesures = request.form.get("nb_mesures", type=int, default=4)
    pistes = request.form.getlist("pistes")
    if f.filename == "":
        return jsonify({"error": "empty filename"}), 400

    # Enregistrer le WAV dans un dossier temporaire
    wav_path = os.path.join(r"recordings", f.filename)  # ou un dossier temp
    f.save(wav_path)

    # Générer le chemin MIDI automatiquement
    midi_path = get_next_midi_path(instrument)

    # Convertir WAV → MIDI

    v2m.convert_wav_to_midi(wav_path, midi_path,bpm,nb_mesures)

    

    #créer le wav du nouvel instru et stock son path 
    instru_n = os.path.basename(midi_path)         
    instru_n_without_ext = os.path.splitext(instru_n)[0] 
    out_track_path = f"./AUDIO/{instru_n_without_ext}.wav"
    new_track = audio_tools.midi_to_wav.midi_to_wav(midi_path, "./GeneralUser-GS.sf2", instrument, out_track_path)


    #crée le mix band avec le nouvel instru et stock son path 
    to_mix = (pistes or []) + [new_track]
    master_path = audio_tools.mixer.mix_wav_files("./AUDIO/master.wav", to_mix)


    
    return jsonify({"master": master_path,
                    "newtrack": new_track} )





        

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9004, debug=True)

