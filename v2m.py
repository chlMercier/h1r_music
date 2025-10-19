from flask import Flask, request, jsonify
import os
import tempfile
import numpy as np
import librosa
from mido import MidiFile, MidiTrack, Message,MetaMessage, bpm2tempo


# Paramètres
HOP_LENGTH = 512
FMIN = 60
FMAX = 1000
MIN_LENGTH = 7  # nouveau min_length
TICKS_PER_BEAT = 480


def hz_to_midi_note(hz):
    return int(round(69 + 12 * np.log2(hz / 440.0)))


def apply_min_length_filter(f1, min_length=MIN_LENGTH):
    """
    Nouveau filtre basé sur la segmentation en notes séparées par des silences.
    Les segments courts sont remplacés par la dernière note valide.
    """
    f1 = np.array(f1, dtype=float)
    filtered = np.full_like(f1, np.nan)
    i = 0
    last_note = np.nan

    while i < len(f1):
        # Si c’est un silence, on passe au suivant
        if np.isnan(f1[i]):
            i += 1
            continue

        # Début d’un segment de note (jusqu’au prochain silence)
        j = i
        while j < len(f1) and not np.isnan(f1[j]):
            j += 1

        segment = f1[i:j]
        count = len(segment)
        note_mean = f1[i:j]
        note_mean = np.nanmean(segment)

        if count >= min_length:
            # Note assez longue → garder la moyenne
            filtered[i:j] = note_mean
            last_note = note_mean
        else:
            # Note trop courte → remplacer par la dernière note valide (si existante)
            if not np.isnan(last_note):
                filtered[i:j] = last_note
            # sinon, on laisse en silence (np.nan)

        i = j  # passage au segment suivant

    return filtered


def filtered_notes_to_midi(filtered, sr, tempo_bpm,
                           ticks_per_beat=TICKS_PER_BEAT,
                           hop_length=HOP_LENGTH,
                           out_path="output.mid"):
    mid = MidiFile(ticks_per_beat=ticks_per_beat)
    microseconds_per_beat = bpm2tempo(tempo_bpm)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage("set_tempo", tempo=microseconds_per_beat))

    # Durée d'un tick en secondes
    seconds_per_tick = 60.0 / (tempo_bpm * ticks_per_beat)

    current_note = None
    duration_seconds = 0.0

    for n in filtered:
        if isinstance(n, float) and np.isnan(n):
            if current_note is not None:
                # Convertir la durée en ticks
                duration_ticks = max(1, int(round(duration_seconds / seconds_per_tick)))
                track.append(Message('note_off', note=int(current_note), velocity=64, time=duration_ticks))
                current_note = None
                duration_seconds = 0.0
            continue

        n_int = int(round(n))
        if current_note == n_int:
            duration_seconds += hop_length / sr
        else:
            if current_note is not None:
                duration_ticks = max(1, int(round(duration_seconds / seconds_per_tick)))
                track.append(Message('note_off', note=int(current_note), velocity=64, time=duration_ticks))
            track.append(Message('note_on', note=n_int, velocity=64, time=0))
            current_note = n_int
            duration_seconds = hop_length / sr

    # Note finale
    if current_note is not None:
        duration_ticks = max(1, int(round(duration_seconds / seconds_per_tick)))
        track.append(Message('note_off', note=int(current_note), velocity=64, time=duration_ticks))

    mid.save(out_path)
    return out_path


def convert_wav_to_midi(wav_path, midi_path,bpm,nb_mesures):
    # Charger l'audio
    duration = nb_mesures*4*60/bpm
    y, sr = librosa.load(wav_path, mono=True,duration=duration)
    #print("sr: ",sr)
    #print("bpm:",bpm)
    #print("duration: ",duration)
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=FMIN, fmax=FMAX)
    times = librosa.times_like(f0)

    # Conversion en notes MIDI (ou np.nan)
    f1 = [hz_to_midi_note(v) if v is not None and not np.isnan(v) else np.nan for v in f0]

    # Appliquer le nouveau filtre min_length
    filtered = apply_min_length_filter(f1, min_length=MIN_LENGTH)

    # Générer le fichier MIDI
    filtered_notes_to_midi(filtered, sr=sr, hop_length=HOP_LENGTH,
                           tempo_bpm=bpm, ticks_per_beat=TICKS_PER_BEAT,
                           out_path=midi_path)   
       

    # Retour simple
    return f"MIDI enregistré : {midi_path}"

convert_wav_to_midi("recordings/music.wav","midi/output1.mid",130,4)