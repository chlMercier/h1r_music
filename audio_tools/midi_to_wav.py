import os
import numpy as np
import soundfile as sf
import pretty_midi
import tempfile

def midi_to_wav(midi_path, soundfont_path, instrument_name, output_path=None, sample_rate=44100):
    """Convertit un fichier MIDI en WAV avec l’instrument choisi."""
    if not os.path.exists(midi_path):
        raise FileNotFoundError(f"❌ Fichier MIDI introuvable : {midi_path}")
    if not os.path.exists(soundfont_path):
        raise FileNotFoundError(f"❌ SoundFont introuvable : {soundfont_path}")

    midi = pretty_midi.PrettyMIDI(midi_path)
    program = pretty_midi.instrument_name_to_program(instrument_name)
    for inst in midi.instruments:
        inst.program = program

    print(f"🎶 Conversion {os.path.basename(midi_path)} → {instrument_name} (sample_rate={sample_rate})")
    audio = midi.fluidsynth(sf2_path=soundfont_path, fs=sample_rate)
    audio = np.clip(audio, -1.0, 1.0)

    if output_path is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        output_path = tmp.name
        tmp.close()

    sf.write(output_path, audio, sample_rate, subtype='PCM_16')
    return output_path
