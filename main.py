# server_convert.py
from flask import Flask, request, send_file ,  jsonify
import os
import tempfile
import numpy as np
import librosa
from mido import MidiFile, MidiTrack, Message
import v2m
import audio_tools.midi_to_wav , audio_tools.mixer


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


def list_files_in_folder(folder_path):
    """Retourne la liste des fichiers dans un dossier donné."""
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"❌ Le dossier '{folder_path}' n'existe pas.")
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]


###################


@app.route("/convert", methods=["POST"])
def convert_wav_to_midi():
    if "file" not in request.files:
        return jsonify({"error": "no file part (form field 'file' missing)"}), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "empty filename"}), 400

    # Enregistrer le WAV dans un dossier temporaire
    wav_path = os.path.join(os.getcwd(), f.filename)  # ou un dossier temp
    f.save(wav_path)

    # Générer le chemin MIDI automatiquement
    midi_path = get_next_midi_path()

    # Convertir WAV → MIDI
    v2m.convert_wav_to_midi(wav_path, midi_path)
    
    instru_name = "Trumpet"

    #créer le wav du nouvel instru et stock son path 
    new_instru_path = audio_tools.midi_to_wav.midi_to_wav(midi_path,"./GeneralUser-GS.sf2",instru_name,"./AUDIO")


    file_path = "./AUDIO/band.wav"

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"🗑️ Fichier supprimé avant regénération: {file_path}")


    #trouve la liste des noms de fichiers dans le dossier audio
    list_files_4_band = list_files_in_folder("./AUDIO")

    #crée le mix band avec le nouvel instru et stock son path 
    new_band_path = audio_tools.mixer.mix_wav_files("./AUDIO/band.wav",list_files_4_band,)


    #zip des deux fichiers wav

    #envoie les wav zippés
    send_file()


    #supprime le fichier band
  


    return jsonify({"message": f"MIDI enregistre: {midi_path}"})


        


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9004, debug=True)

