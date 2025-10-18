import numpy as np
import soundfile as sf
import os

def mix_wav_files(output_path, wav_paths, volumes=None, sample_rate=44100):
    """Fusionne plusieurs fichiers WAV en un seul mix stéréo."""
    if not wav_paths:
        raise ValueError("Aucun fichier WAV fourni pour le mixage.")
    if volumes is None:
        volumes = [100] * len(wav_paths)
    if len(volumes) != len(wav_paths):
        raise ValueError("Le nombre de volumes doit correspondre au nombre de fichiers WAV.")

    tracks = []
    for path, vol in zip(wav_paths, volumes):
        if not os.path.exists(path):
            print(f"⚠️ Fichier introuvable : {path}")
            continue
        data, sr = sf.read(path)
        if sr != sample_rate:
            print(f"⚠️ Taux d’échantillonnage différent ({sr}), conversion implicite.")
        if data.ndim == 1:
            data = np.column_stack([data, data])
        data = data.astype(np.float32) * (vol / 100.0)
        tracks.append(data)

    if not tracks:
        raise RuntimeError("❌ Aucun fichier audio valide à mixer.")

    max_len = max(t.shape[0] for t in tracks)
    mix = np.zeros((max_len, 2), dtype=np.float32)
    for t in tracks:
        mix[:t.shape[0]] += t

    max_amp = np.max(np.abs(mix))
    if max_amp > 0:
        mix /= max_amp

    sf.write(output_path, mix, sample_rate)
    print(f"✅ Mix créé : {output_path} ({sample_rate} Hz)")
    return output_path
