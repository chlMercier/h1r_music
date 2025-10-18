
from flask import Flask, request, jsonify
import os
import tempfile
import numpy as np
import librosa
from mido import MidiFile, MidiTrack, Message

# Paramètres
HOP_LENGTH = 512
FMIN = 60
FMAX = 1000
MIN_LENGTH = 10
TEMPO_BPM = 120
TICKS_PER_BEAT = 480

def hz_to_midi_note(hz):
    return int(round(69 + 12 * np.log2(hz / 440.0)))

def apply_min_length_filter(f1, min_length=MIN_LENGTH):
    filtered = []
    i = 0
    last_note = np.nan
    N = len(f1)

    while i < N:
        note = f1[i]
        count = 1
        while i + count < N:
            next_note = f1[i + count]
            if (isinstance(note, float) and np.isnan(note) and isinstance(next_note, float) and np.isnan(next_note)) \
                or (note == next_note):
                count += 1
            else:
                break

        if count >= min_length:
            filtered.extend([note]*count)
            if not (isinstance(note, float) and np.isnan(note)):
                last_note = note
        else:
            replacement = last_note
            filtered.extend([replacement]*count)

        i += count 

    return filtered

def filtered_notes_to_midi(filtered, sr, hop_length=HOP_LENGTH, tempo_bpm=TEMPO_BPM,
                           ticks_per_beat=TICKS_PER_BEAT, out_path="output.mid"):
    mid = MidiFile(ticks_per_beat=ticks_per_beat)
    track = MidiTrack()
    mid.tracks.append(track)

    frame_ticks = max(1, int(round((hop_length / sr) * (ticks_per_beat / (60.0/tempo_bpm)))))
    current_note = None
    duration_ticks = 0

    for n in filtered:
        if isinstance(n, float) and np.isnan(n):
            if current_note is not None:
                track.append(Message('note_off', note=int(current_note), velocity=64, time=duration_ticks))
                current_note = None
                duration_ticks = 0
            continue

        n_int = int(n)
        if current_note == n_int:
            duration_ticks += frame_ticks
        else:
            if current_note is not None:
                track.append(Message('note_off', note=int(current_note), velocity=64, time=duration_ticks))
            track.append(Message('note_on', note=n_int, velocity=64, time=0))
            current_note = n_int
            duration_ticks = frame_ticks

    if current_note is not None:
        track.append(Message('note_off', note=int(current_note), velocity=64, time=duration_ticks))

    mid.save(out_path)
    return out_path


def convert_wav_to_midi(wav_path,midi_path):
 # Charger audio
    y, sr = librosa.load(wav_path, sr=None, mono=True)
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=FMIN, fmax=FMAX, hop_length=HOP_LENGTH)

        # Conversion en notes MIDI (ou np.nan)
    f1 = [hz_to_midi_note(v) if v is not None and not np.isnan(v) else np.nan for v in f0]

        # Appliquer filtre min_length
    filtered = apply_min_length_filter(f1, min_length=MIN_LENGTH)

        # Générer le fichier MIDI
    filtered_notes_to_midi(filtered, sr=sr, hop_length=HOP_LENGTH,
                            tempo_bpm=TEMPO_BPM, ticks_per_beat=TICKS_PER_BEAT,
                            out_path=midi_path)    
       

    # Retour simple
    return f"MIDI enregistré : {midi_path}"