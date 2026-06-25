# portfolio-insans

This project was built with Turbo 360. To learn more, click here: https://www.turbo360.co

## Instructions
After cloning into repo, cd to project root directory and install dependencies:

```
$ npm install
```

To run dev server, install Turbo CLI globally:

```
$ sudo npm install turbo-cli -g
```

Then run devserver from project root directory:

```
$ turbo devserver
```

To build for production, run build:

```
$ npm run build
```

## Local Llama Voice Over (Python)

Repo ini sekarang juga memiliki aplikasi Python mandiri untuk voice over AI lokal dengan 2 mode:

- **Mode teks / CLI** untuk membuat audio langsung dari terminal
- **Mode web** untuk memasukkan teks lewat browser

Fitur ini memakai **Llama lokal via Ollama** untuk merapikan naskah sesuai karakter suara, lalu memakai TTS lokal (`espeak-ng`, `espeak`, atau command kustom dari `VOICEOVER_TTS_COMMAND`) untuk menghasilkan audio.

### Jalankan mode web

```bash
python3 local_llama_voiceover.py --mode web
```

Lalu buka `http://127.0.0.1:8000`.

### Jalankan mode teks / CLI

```bash
python3 local_llama_voiceover.py --mode text --text "Halo, selamat datang" --character "Narator hangat"
```

### Konfigurasi opsional

- `OLLAMA_MODEL` - model lokal yang dipakai, default `llama3.1`
- `OLLAMA_URL` - endpoint generate Ollama, default `http://127.0.0.1:11434/api/generate`
- `VOICEOVER_TTS_COMMAND` - command TTS kustom. Gunakan placeholder `{output}`, `{text}`, dan `{voice}` bila perlu.
