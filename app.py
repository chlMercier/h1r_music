import sys
from audio_tools.midi_to_wav import midi_to_wav
from audio_tools.mixer import mix_wav_files

def m2v(output_wav,soundfront,sample_rate,pairs):
    output_wav = sys.argv[1]
    soundfont = sys.argv[2]
    sample_rate = int(sys.argv[3])
    pairs = sys.argv[4:]

    if len(pairs) % 2 != 0:
        print("❌ Les arguments doivent être sous la forme <midi> <instrument>.")
        sys.exit(1)

    wavs = []
    for i in range(0, len(pairs), 2):
        midi_path = pairs[i]
        instrument = pairs[i + 1]
        wav_path = midi_to_wav(midi_path, soundfont, instrument, sample_rate=sample_rate)
        wavs.append(wav_path)

    mix_wav_files(output_wav, wavs, sample_rate=sample_rate)
    print(f"🎵 Mix final disponible : {output_wav}")

if __name__ == "__main__":
    main()
