# AI Voice Over

Aplikasi **voice over** berbasis AI lokal (LLama via Ollama) dengan antarmuka web dan CLI.  
User memasukkan teks → AI memprosesnya sesuai karakter → suara manusiawi dihasilkan.

---

## Fitur

| Fitur | Keterangan |
|---|---|
| 🤖 AI Narasi | Teks diproses oleh LLama lokal untuk narasi yang alami sesuai karakter AI |
| 🎙️ Multi-karakter | Friendly · Professional · Storyteller · Assistant |
| 🔊 Edge TTS | Suara manusiawi berkualitas tinggi (online) |
| 📢 pyttsx3 | TTS offline sebagai fallback |
| 🌐 Mode Web | Antarmuka browser penuh (FastAPI) |
| 💻 Mode CLI/Teks | Masukan teks via argumen, stdin, atau mode interaktif |

---

## Prasyarat

1. **Python 3.10+**
2. **Ollama** berjalan lokal dengan model LLama:
   ```bash
   # Install Ollama: https://ollama.com
   ollama pull llama3
   ollama serve          # pastikan berjalan di http://localhost:11434
   ```
3. *(Opsional)* Koneksi internet untuk Edge TTS.

---

## Instalasi

```bash
cd voiceover
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Menjalankan Aplikasi

### Mode Web (browser)

```bash
uvicorn app:app --reload --port 8000
```

Buka **http://localhost:8000** di browser.

### Mode CLI / Teks

```bash
# Teks langsung sebagai argumen
python cli.py "Selamat datang di aplikasi voice over AI!"

# Mode interaktif (terus meminta input)
python cli.py --interactive

# Membaca dari stdin
echo "Hari ini cerah sekali." | python cli.py

# Simpan audio ke file (tanpa memutar)
python cli.py "Hello world" --output output.mp3

# Karakter profesional, suara British
python cli.py "Good evening." --character professional --voice en-GB-SoniaNeural

# Suara Indonesia
python cli.py "Selamat pagi, apa kabar?" --voice id-ID-GadisNeural

# TTS offline (tanpa internet), tanpa LLM
python cli.py "Halo dunia" --engine pyttsx3 --no-llm

# Lihat model Ollama yang tersedia
python cli.py --list-models
```

---

## Opsi CLI

| Opsi | Default | Keterangan |
|---|---|---|
| `text` | *(stdin)* | Teks yang akan diubah menjadi suara |
| `--model` | `llama3` | Model Ollama yang digunakan |
| `--character` | `friendly` | Karakter AI: `friendly`, `professional`, `storyteller`, `assistant` |
| `--engine` | `edge_tts` | Mesin TTS: `edge_tts` atau `pyttsx3` |
| `--voice` | `en-US-JennyNeural` | Nama suara Edge TTS |
| `--no-llm` | *(off)* | Lewati pemrosesan LLM, langsung ke TTS |
| `--output`, `-o` | *(play)* | Simpan audio ke file |
| `--interactive`, `-i` | *(off)* | Mode interaktif terus-menerus |
| `--list-models` | *(off)* | Tampilkan model Ollama lokal lalu keluar |

---

## Suara Edge TTS yang Tersedia (Contoh)

| Kode Suara | Bahasa | Jenis Kelamin |
|---|---|---|
| `en-US-JennyNeural` | Inggris (AS) | Wanita |
| `en-US-GuyNeural` | Inggris (AS) | Pria |
| `en-GB-SoniaNeural` | Inggris (UK) | Wanita |
| `en-AU-NatashaNeural` | Inggris (AU) | Wanita |
| `id-ID-GadisNeural` | Indonesia | Wanita |
| `id-ID-ArdiNeural` | Indonesia | Pria |

Untuk daftar lengkap suara, gunakan endpoint `/api/voices` saat server berjalan.

---

## Arsitektur

```
voiceover/
├── app.py              # FastAPI web app (mode web)
├── cli.py              # CLI entrypoint (mode teks)
├── core/
│   ├── llm.py          # Integrasi Ollama / LLama
│   └── tts.py          # Mesin TTS (edge_tts & pyttsx3)
├── templates/
│   └── index.html      # UI Web
├── static/
│   ├── style.css
│   └── script.js
└── requirements.txt
```

---

## Alur Kerja

```
User Input (teks)
      │
      ▼
 [LLM – Ollama]  ← karakter AI memformat narasi alami
      │
      ▼
 [TTS Engine]    ← edge_tts (online) / pyttsx3 (offline)
      │
      ▼
 Audio Output    ← diputar langsung atau disimpan ke file
```
