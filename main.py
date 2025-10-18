# server_convert.py
from flask import Flask, request, jsonify
import os
import tempfile
import numpy as np
import librosa
from mido import MidiFile, MidiTrack, Message
import v2m

app = Flask(__name__)


@app.route("/convert", methods=["POST"])
def convert_wav_to_midi():
    if "file" not in request.files:
        return jsonify({"error": "no file part (form field 'file' missing)"}), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "empty filename"}), 400

    # Répertoire temporaire pour WAV
    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = os.path.join(tmpdir, "hymne.wav")
        midi_path = r"C:\Users\Utilisateur\Documents\hack1robot\output2.mid"  # chemin fixe Windows

        f.save(wav_path)
        return v2m.convert_wav_to_midi(wav_path,midi_path)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9004, debug=True)
