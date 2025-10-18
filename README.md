# MUSIC Hack1robo

Projet Music pour Hack1robo

## Installation via poetry

1. Install poetry (`pip install poetry`)

2. Install dependencies (`poetry install`)

3. Activate virtual environment:

Bash:

```
$eval $(poetry env activate)
(h1rmusic) $  # Virtualenv entered
```

Powershell:

```
PS1> Invoke-Expression (poetry env activate)
(h1rmusic) PS1>  # Virtualenv entered
```

4. Run within virtual env:

```
(h1rmusic) $  poetry run python blabla.py
```

### activate virtual env with pip on windows:

```
venv\Scripts\Activate.ps1

```

## Recording sound

(All of these can be replaced with poetry run command if the virtual env is activated)

```
$ python record-sound.py
```

Records your voice until you type Ctrl+C. The record is stored in to recordings/.

## Convert WAV into MIDI

```
# start server
$ python main.py
# in another terminal:
$ curl.exe -X POST -F "audio=@./recordings/hymne-a-la-joie.wav" http://localhost:9004/convert
```
