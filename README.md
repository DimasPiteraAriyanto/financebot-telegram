# FinanceBot Telegram 🤖📊

FinanceBot adalah bot Telegram untuk manajemen keuangan pribadi serba cepat & gratis. Mencatat pemasukan, pengeluaran, bukti struk transaksi, anggaran (budget), dan laporan grafik langsung via Telegram dan tersimpan otomatis di Google Sheets.

---

## 🌟 Fitur Utama

- ⚡ **Pencatatan < 5 Detik**:
  - Pengeluaran: `-25000 makan siang` atau `-25k kopi`
  - Pemasukan: `+5000000 gaji juli` atau `+5jt bonus`
  - Smart Detection: `bakso 25000` (konfirmasi tombol otomatis)
- 📊 **Laporan Lengkap**:
  - `/saldo` — Cek saldo saat ini & ringkasan bulanan.
  - `/today` — Rekap detail transaksi hari ini.
  - `/week` — Rekap 7 hari terakhir & perbandingan minggu lalu.
  - `/month` — Cashflow bulanan net & top kategori.
- 📈 **Grafik & Diagram (Matplotlib)**:
  - `/chart` — Pilihan Pie Chart, Bar Chart, & Cashflow.
- 🎯 **Budget Management**:
  - `/budget` — Monitoring batas anggaran dengan ASCII progress bar (`████████░░ 80%`).
  - `/budget set <kategori> <nominal>` — Menetapkan batas budget baru.
  - Auto-warning saat anggaran mencapai 80% dan 100%.
- 📷 **Upload Bukti Transaksi (Google Drive)**:
  - Kirim foto struk/transfer di chat → otomatis terupload & terhubung ke transaksi.
- 📂 **Export Data**:
  - `/export` — Unduh seluruh data transaksi dalam format file CSV.
- 🔔 **Pengingat Otomatis (APScheduler)**:
  - Daily Reminder (20:00) jika belum catat transaksi.
  - Daily Summary (21:00) ringkasan hari ini.

---

## 🚀 Panduan Setup & Instalasi Lokal

### 1. Prasyarat
- Python 3.12+
- Akun Telegram
- Akun Google Cloud (untuk Google Sheets & Drive API)

### 2. Clone & Setup Virtual Environment
```bash
git clone https://github.com/yourusername/python-bot.git
cd python-bot

# Buat virtual environment
python -m venv .venv

# Aktivasi virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Install dependensi
pip install -r requirements.txt
```

### 3. Konfigurasi Bot Telegram (@BotFather)
1. Buka Telegram dan cari **@BotFather**.
2. Ketik `/newbot` dan ikuti petunjuk untuk membuat bot baru.
3. Dapatkan **HTTP API Token** (contoh: `123456789:ABCdefGHIjklMNOpqrsTUVwxyZ`).

### 4. Setup Google API Credentials (`credentials.json`)
1. Buka [Google Cloud Console](https://console.cloud.google.com/).
2. Buat project baru, aktifkan **Google Sheets API** & **Google Drive API**.
3. Buat **Service Account** di menu Credentials -> Create Credentials -> Service Account.
4. Buat Key baru format **JSON** dan simpan file tersebut sebagai `credentials.json` di root folder project.

### 5. Pengisian File Environment (`.env`)
Salin file `.env.example` menjadi `.env`:
```bash
cp .env.example .env
```
Isi file `.env` dengan kredensial Anda:
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyZ
ALLOWED_USER_IDS=123456789
GOOGLE_CREDENTIALS_FILE=credentials.json
SPREADSHEET_NAME=FinanceBot_Database
TIMEZONE=Asia/Jakarta
CURRENCY=IDR
```

### 6. Jalankan Unit Tests
```bash
python -m unittest discover -s tests
```

### 7. Jalankan Bot
```bash
python bot.py
```

---

## ☁️ Panduan Deployment Gratis 24/7

### Opsi A: Railway (Rekomendasi)
1. Push project Anda ke repository GitHub.
2. Login ke [Railway.app](https://railway.app/).
3. Buat New Project -> Deploy from GitHub repo.
4. Masukkan **Variables** di Dashboard Railway sesuai isi `.env`.
5. Upload atau masukkan isi `credentials.json` via environment variable atau Secret Files.
6. Railway akan meng-build dan menjalankan bot 24/7 secara otomatis.

### Opsi B: Render.com
1. Buat **Background Worker** baru di Render.
2. Hubungkan repository GitHub Anda.
3. Set Build Command: `pip install -r requirements.txt`.
4. Set Start Command: `python bot.py`.
5. Masukkan Environment Variables di Setting.

---

## 📁 Struktur Folder Project

```text
financebot/
├── bot.py                  # Main entrypoint Telegram bot polling
├── config.py               # Application configuration
├── requirements.txt        # Python package dependencies
├── .env.example            # Template environment variables
├── .gitignore              # Git ignore configuration
├── README.md               # Production documentation
│
├── constants/
│   ├── categories.py       # Default category list & keyword detection
│   └── messages.py         # Response text templates
│
├── services/
│   ├── sheets.py           # Google Sheets API & local mock fallback
│   ├── parser.py           # Transaction parser & smart detection
│   ├── report.py           # Financial reporting aggregator
│   ├── charts.py           # Matplotlib chart buffer generator
│   ├── budget.py           # Budget tracking & threshold warning
│   ├── drive.py            # Google Drive upload manager
│   └── scheduler.py        # APScheduler daily cron jobs
│
├── handlers/
│   ├── start.py            # /start and /help handlers
│   ├── transaction.py      # Transaction input & inline callbacks
│   ├── report.py           # /saldo, /today, /week, /month, /hapus
│   ├── chart.py            # /chart command & image callback handler
│   ├── budget.py           # /budget and /budget set handlers
│   ├── receipt.py          # Photo receipt message handler
│   ├── export.py           # /export CSV handler
│   └── settings.py         # /settings handler
│
├── utils/
│   ├── formatter.py        # Currency & shortcut amount parser
│   ├── validator.py        # User authorization & input sanitizer
│   ├── cache.py            # TTL memory cache manager
│   └── logger.py           # Application logger
│
└── tests/                  # Automated unit test suite
    ├── test_parser.py
    ├── test_report.py
    ├── test_chart_budget.py
    └── test_automation.py
```

---

## 📜 Lisensi
MIT License © 2026 FinanceBot Team
