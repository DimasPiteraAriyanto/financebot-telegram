# PRODUCT REQUIREMENTS DOCUMENT (PRD)

# FinanceBot Telegram v2.0

## Personal Finance Management Bot — 100% Free Stack

**Version:** 2.0 (Revised)
**Status:** Development Plan
**Platform:** Telegram Bot
**Primary Storage:** Google Sheets (Free 15GB)
**File Storage:** Google Drive (Free 15GB)
**Backend:** Python 3.12+
**Hosting:** Railway Free Tier / Render / Oracle Cloud Free
**Last Updated:** 31 Juli 2026

---

# 1. Product Overview

## 1.1 Deskripsi

FinanceBot adalah bot Telegram untuk mencatat pemasukan dan pengeluaran pribadi melalui shortcut sederhana. Semua data tersimpan di Google Sheets (gratis) dan bukti transaksi di Google Drive (gratis).

## 1.2 Kenapa Telegram?

| Alasan | Detail |
|--------|--------|
| **Sudah terinstall** | 700+ juta user aktif, tidak perlu install app baru |
| **Cepat** | Input transaksi < 5 detik via chat |
| **Gratis** | Bot API unlimited & gratis |
| **Notifikasi** | Push notification bawaan |
| **File support** | Upload foto receipt langsung |

---

# 2. Problem & Solution

## Problem

| # | Masalah | Impact |
|---|---------|--------|
| 1 | App keuangan terlalu ribet, banyak langkah | User malas buka app |
| 2 | Pencatatan manual sering lupa | Data keuangan tidak akurat |
| 3 | Bukti transaksi tersebar di galeri/chat | Susah lacak pengeluaran |
| 4 | Tidak ada insight pengeluaran | Tidak tahu kemana uang pergi |

## Solution

| # | Solusi | Cara |
|---|--------|------|
| 1 | Input 5 detik | Ketik `-25000 makan` di Telegram |
| 2 | Auto reminder | Bot ingatkan jika belum catat hari ini |
| 3 | Upload receipt | Foto → otomatis ke Google Drive |
| 4 | Auto report + chart | Bot kirim grafik pengeluaran |

---

# 3. Target User

**Primary:** Individu yang ingin track keuangan pribadi (1-10 user awal)

> **NOTE:** Bot ini didesain untuk penggunaan personal/small group. Google Sheets API memiliki limit 300 request/menit yang cukup untuk < 10 user aktif.

---

# 4. Tech Stack (100% Free)

| Layer | Teknologi | Biaya |
|-------|-----------|-------|
| Bot Framework | `python-telegram-bot` v21+ | Free |
| Database | Google Sheets API v4 | Free (300 req/min) |
| File Storage | Google Drive API v3 | Free (15GB) |
| Data Processing | Pandas, NumPy | Free |
| Visualization | Matplotlib, Plotly | Free |
| Scheduler | APScheduler | Free |
| Config | python-dotenv | Free |
| Auth | `gspread` + Service Account | Free |
| Hosting | Railway / Render / Oracle Cloud | Free tier |
| Cache | In-memory dict (local cache) | Free |

---

# 5. System Architecture

```
┌─────────────┐
│  User        │
│  (Telegram)  │
└──────┬───────┘
       │ Message/Photo
       ▼
┌──────────────┐
│ Telegram API │
└──────┬───────┘
       │ Webhook / Polling
       ▼
┌──────────────────────────────────────────────┐
│            Python Backend                     │
│                                               │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │ Handlers │  │ Services │  │   Utils     │ │
│  │----------│  │----------│  │------------│ │
│  │/start    │  │sheets.py │  │validator.py│ │
│  │/saldo    │→ │drive.py  │  │formatter.py│ │
│  │/laporan  │  │parser.py │  │cache.py    │ │
│  │/budget   │  │charts.py │  │logger.py   │ │
│  │/chart    │  │scheduler │  │            │ │
│  └──────────┘  └────┬─────┘  └────────────┘ │
│                     │                         │
└─────────────────────┼─────────────────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
   ┌──────────┐ ┌──────────┐ ┌────────┐
   │ Google   │ │ Google   │ │ Local  │
   │ Sheets   │ │ Drive    │ │ Cache  │
   │(Database)│ │(Receipt) │ │(Memory)│
   └──────────┘ └──────────┘ └────────┘
```

### Data Flow — Input Transaksi

```
User ketik: "-25000 makan siang"
       │
       ▼
┌─ Parser Service ──────────────────────┐
│ 1. Detect prefix (+/-)                │
│ 2. Extract amount: 25000              │
│ 3. Extract note: "makan siang"        │
│ 4. Auto-categorize: "Food" 🍜         │
│ 5. Generate Transaction ID            │
└───────────────┬───────────────────────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
  ┌─────────┐    ┌──────────────┐
  │ Cache   │    │ Google Sheets│
  │ Update  │    │ Append Row   │
  └─────────┘    └──────────────┘
                         │
                         ▼
                 ┌──────────────┐
                 │ Bot Response │
                 │ ✅ Tercatat  │
                 └──────────────┘
```

---

# 6. Project Structure

```
financebot/
│
├── bot.py                  # Entry point, bot initialization
├── config.py               # Configuration & environment variables
├── requirements.txt        # Python dependencies
├── .env                    # Secrets (TIDAK masuk git)
├── .env.example            # Template env
├── credentials.json        # Google Service Account (TIDAK masuk git)
├── .gitignore
├── README.md
│
├── handlers/               # Telegram command & message handlers
│   ├── __init__.py
│   ├── start.py            # /start, /help
│   ├── transaction.py      # Input pemasukan/pengeluaran
│   ├── report.py           # /saldo, /today, /week, /month
│   ├── budget.py           # /budget
│   ├── chart.py            # /chart
│   ├── receipt.py          # Upload foto bukti
│   └── settings.py         # /settings
│
├── services/               # Business logic
│   ├── __init__.py
│   ├── sheets.py           # Google Sheets CRUD + caching
│   ├── drive.py            # Google Drive upload
│   ├── parser.py           # Input parser & category detection
│   ├── charts.py           # Chart generation (matplotlib/plotly)
│   ├── scheduler.py        # Reminder & scheduled reports
│   └── budget.py           # Budget tracking logic
│
├── utils/                  # Utilities
│   ├── __init__.py
│   ├── formatter.py        # Currency & date formatting
│   ├── validator.py        # Input validation
│   ├── cache.py            # In-memory cache manager
│   └── logger.py           # Logging configuration
│
├── constants/              # Constants & enums
│   ├── __init__.py
│   ├── categories.py       # Category definitions & keywords
│   └── messages.py         # Bot response templates
│
└── tests/                  # Unit tests
    ├── test_parser.py
    ├── test_sheets.py
    └── test_budget.py
```

---

# 7. Google Sheets Database Design

## 7.1 Sheet: `Transactions`

| Column | Type | Example | Keterangan |
|--------|------|---------|------------|
| `id` | String | `TXN-20260731-001` | Auto-generated |
| `date` | Date | `2026-07-31` | Tanggal transaksi |
| `time` | Time | `14:30:00` | Waktu transaksi |
| `type` | String | `expense` / `income` | Jenis transaksi |
| `category` | String | `Food` | Kategori |
| `amount` | Number | `25000` | Nominal (selalu positif) |
| `note` | String | `makan siang` | Catatan user |
| `receipt_url` | String | `https://drive.google...` | Link foto bukti |
| `balance` | Number | `4975000` | Running balance |
| `created_at` | DateTime | `2026-07-31T14:30:00` | Timestamp |

## 7.2 Sheet: `Categories`

| Column | Example |
|--------|---------|
| `name` | Food |
| `emoji` | 🍜 |
| `type` | expense |
| `keywords` | makan,bakso,nasi,kopi,minum,restoran,warteg |

**Default Categories:**

| Category | Emoji | Type | Keywords |
|----------|-------|------|----------|
| Food | 🍜 | expense | makan, bakso, nasi, kopi, minum, restoran, warteg, goFood |
| Transport | 🚗 | expense | gojek, grab, bensin, parkir, tol, bus, kereta, ojek |
| Shopping | 🛒 | expense | beli, belanja, shopee, tokped, lazada |
| Health | 💊 | expense | obat, dokter, rumah sakit, apotek |
| Entertainment | 🎮 | expense | nonton, game, spotify, netflix, hiburan |
| Bills | 📱 | expense | listrik, air, internet, pulsa, wifi |
| Education | 📚 | expense | buku, kursus, kuliah, les |
| Salary | 💼 | income | gaji, salary |
| Freelance | 💻 | income | project, freelance, klien |
| Transfer | 💸 | income | transfer, kiriman |
| Other Income | 💰 | income | bonus, hadiah, cashback |
| Other Expense | 📦 | expense | lainnya |

## 7.3 Sheet: `Budget`

| Column | Example |
|--------|---------|
| `category` | Food |
| `monthly_limit` | 2000000 |
| `current_usage` | 750000 |
| `month` | 2026-07 |

## 7.4 Sheet: `Settings`

| Column | Example |
|--------|---------|
| `user_id` | 123456789 |
| `currency` | IDR |
| `timezone` | Asia/Jakarta |
| `reminder_time` | 21:00 |
| `language` | id |

---

# 8. Core Features

## 8.1 Input Transaksi (Primary Feature)

### Format Input — Standardized

```
# PENGELUARAN (wajib prefix -)
-25000 makan siang
-15000 gojek kantor
-150000 belanja bulanan

# PEMASUKAN (wajib prefix +)
+5000000 gaji juli
+500000 freelance project
```

### Smart Detection (Secondary — dengan konfirmasi)

```
# User ketik tanpa prefix:
bakso 25000

# Bot konfirmasi via Inline Keyboard:
┌─────────────────────────────────────┐
│ Transaksi terdeteksi:               │
│                                     │
│ 📝 bakso                            │
│ 💰 Rp25.000                         │
│ 📁 Food 🍜                          │
│                                     │
│ Jenis transaksi?                    │
│                                     │
│ [➖ Pengeluaran]  [➕ Pemasukan]     │
│                                     │
│ [❌ Batal]                           │
└─────────────────────────────────────┘
```

### Bot Response — Sukses

```
✅ Transaksi Tercatat!

📁 Kategori  : Food 🍜
💰 Nominal   : Rp25.000
📝 Catatan   : makan siang
📅 Tanggal   : 31 Jul 2026, 14:30

💳 Saldo     : Rp4.975.000

[📷 Tambah Bukti]  [❌ Hapus]  [✏️ Edit]
```

### Bot Response — Error

```
❌ Format tidak dikenali

Cara pakai:
  -25000 makan siang  → pengeluaran
  +5000000 gaji       → pemasukan

Ketik /help untuk bantuan lengkap
```

---

## 8.2 Commands

| Command | Fungsi | Phase |
|---------|--------|-------|
| `/start` | Registrasi & welcome | 1 |
| `/help` | Panduan penggunaan | 1 |
| `/saldo` | Lihat saldo saat ini | 2 |
| `/today` | Laporan hari ini | 2 |
| `/week` | Laporan minggu ini | 2 |
| `/month` | Laporan bulan ini | 2 |
| `/chart` | Kirim grafik pengeluaran | 3 |
| `/budget` | Set & lihat budget | 3 |
| `/budget set Food 2000000` | Set budget per kategori | 3 |
| `/receipt` | Upload bukti transaksi | 3 |
| `/export` | Export data ke CSV | 4 |
| `/settings` | Pengaturan bot | 4 |
| `/hapus` | Hapus transaksi terakhir | 2 |
| `/undo` | Undo transaksi terakhir | 2 |

---

## 8.3 Reporting System

### `/saldo` Response

```
💳 Saldo Keuangan

Saldo saat ini: Rp4.975.000

📊 Bulan ini:
  ➕ Pemasukan : Rp5.500.000
  ➖ Pengeluaran: Rp525.000

📅 Terakhir dicatat: 31 Jul 2026
```

### `/today` Response

```
📋 Laporan Hari Ini — 31 Jul 2026

➕ Pemasukan: Rp0
➖ Pengeluaran: Rp65.000

Detail:
  🍜 -Rp25.000  makan siang
  🚗 -Rp15.000  gojek
  🍜 -Rp25.000  kopi

Total transaksi: 3
```

### `/week` Response

```
📋 Laporan Minggu Ini
28 Jul - 31 Jul 2026

➕ Pemasukan  : Rp5.000.000
➖ Pengeluaran: Rp325.000
📊 Net        : +Rp4.675.000

Top Pengeluaran:
  1. 🍜 Food      : Rp175.000 (53.8%)
  2. 🚗 Transport : Rp100.000 (30.8%)
  3. 📱 Bills     : Rp50.000  (15.4%)

vs Minggu lalu: ⬇️ -12% pengeluaran
```

### `/month` Response

```
📋 Laporan Bulanan — Juli 2026

💰 CASHFLOW
  ➕ Pemasukan  : Rp10.500.000
  ➖ Pengeluaran: Rp3.250.000
  📊 Net        : +Rp7.250.000
  💳 Saldo      : Rp4.975.000

📊 BUDGET STATUS
  🍜 Food      : ████████░░ 80% (Rp1.6jt/2jt)
  🚗 Transport : ██████░░░░ 60% (Rp600rb/1jt)
  🛒 Shopping  : ███░░░░░░░ 30% (Rp300rb/1jt)

🏆 TOP PENGELUARAN
  1. Food       : Rp1.600.000
  2. Transport  : Rp600.000
  3. Shopping   : Rp300.000

📈 Total Transaksi: 87
```

---

## 8.4 Visualization (Charts)

### `/chart` — Inline Keyboard Menu

```
📊 Pilih jenis grafik:

[🥧 Pie Chart]     [📊 Bar Chart]
[📈 Line Chart]    [💰 Cashflow]
[📅 Minggu ini]    [📅 Bulan ini]
```

| Chart | Data | Library |
|-------|------|---------|
| **Pie Chart** | % pengeluaran per kategori | Matplotlib |
| **Bar Chart** | Perbandingan kategori | Matplotlib |
| **Line Chart** | Trend harian pengeluaran | Plotly → PNG |
| **Cashflow** | Income vs Expense per minggu | Matplotlib |

> Chart digenerate sebagai PNG image dan dikirim via Telegram `send_photo`.

---

## 8.5 Receipt Management

### Flow

```
User kirim foto
       │
       ▼
Bot: "📷 Ini bukti untuk transaksi mana?"
       │
       ▼
┌─────────────────────────────────────┐
│ Pilih transaksi:                    │
│                                     │
│ [🍜 -Rp25.000 makan siang (14:30)] │
│ [🚗 -Rp15.000 gojek (13:00)]       │
│ [📝 Transaksi baru]                 │
└─────────────────────────────────────┘
       │
       ▼
Upload ke Google Drive → Simpan URL ke Sheets
       │
       ▼
Bot: "✅ Bukti tersimpan untuk: makan siang Rp25.000"
```

---

## 8.6 Budget Management

### Set Budget

```
/budget set Food 2000000
```

Response:

```
✅ Budget Food ditetapkan: Rp2.000.000/bulan
```

### Budget Warning (Otomatis)

```
⚠️ PERINGATAN BUDGET

🍜 Food sudah mencapai 80%!
Terpakai: Rp1.600.000 / Rp2.000.000
Sisa: Rp400.000

Hati-hati pengeluaran di kategori ini.
```

### Budget Exceeded

```
🚨 BUDGET TERLAMPAUI!

🍜 Food melebihi budget!
Terpakai: Rp2.150.000 / Rp2.000.000
Over: Rp150.000

Transaksi tetap dicatat.
```

---

## 8.7 Notification System

### Daily Reminder (Default 20:00)

```
👋 Hai! Belum ada transaksi hari ini.

Sudah ada pengeluaran yang lupa dicatat?
Ketik langsung, contoh: -25000 makan

[⏭ Lewati Hari Ini]
```

### Daily Summary (Default 21:00)

```
📋 Ringkasan Hari Ini — 31 Jul 2026

➕ Pemasukan  : Rp0
➖ Pengeluaran: Rp65.000
💳 Saldo      : Rp4.975.000

Transaksi: 3
Top: 🍜 Food (Rp50.000)

Selamat malam! 🌙
```

---

# 9. Security

| Aspek | Implementasi |
|-------|-------------|
| **Auth** | Telegram User ID whitelist di `.env` |
| **Secrets** | Token & credentials di `.env`, TIDAK masuk Git |
| **Google Drive** | Private folder, akses hanya via service account |
| **Logging** | Tidak log data sensitif (amount, balance) |
| **Rate Limit** | Max 30 transaksi/menit per user |
| **Data** | Semua data milik user, bisa export kapan saja |

---

# 10. Error Handling Strategy

| Skenario | Handling |
|----------|----------|
| Google Sheets API timeout | Retry 3x dengan exponential backoff, cache transaksi lokal |
| Google Sheets API quota exceeded | Queue transaksi, batch write tiap 5 menit |
| Invalid input format | Kirim pesan error + contoh format benar |
| Google Drive upload gagal | Simpan foto lokal, retry upload di background |
| Bot crash | Auto-restart via hosting platform |
| Duplicate transaction | Check cache, konfirmasi ke user |

---

# 11. Google API Quota Management

```
┌────────────────────────────────────────────┐
│         QUOTA MANAGEMENT STRATEGY          │
│                                            │
│  Google Sheets API: 300 req/min (free)     │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │ WRITE Operations                     │  │
│  │ • Batch append (kumpulkan 5 menit)   │  │
│  │ • Max 60 write/min                   │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │ READ Operations                      │  │
│  │ • In-memory cache (TTL: 5 menit)     │  │
│  │ • Lazy load (baca hanya saat perlu)  │  │
│  │ • Cache saldo, categories, budget    │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │ SAFETY                               │  │
│  │ • Rate limiter per user              │  │
│  │ • Graceful degradation jika limit    │  │
│  │ • Queue + retry mechanism            │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
```

---

# 12. Development Phases

---

## Phase 1 — Foundation & Core Transaction ⚙️

**Durasi:** 1-2 minggu
**Goal:** Bot aktif, user bisa catat transaksi, data masuk Google Sheets

### Tasks

| # | Task | Detail | Priority |
|---|------|--------|----------|
| 1.1 | Setup project structure | Buat folder structure, `requirements.txt`, `.gitignore` | 🔴 Critical |
| 1.2 | Setup Telegram Bot | Buat bot via BotFather, dapatkan token, test koneksi | 🔴 Critical |
| 1.3 | Setup Google API | Buat service account, enable Sheets & Drive API, download `credentials.json` | 🔴 Critical |
| 1.4 | `config.py` | Load `.env`, setup constants | 🔴 Critical |
| 1.5 | `services/sheets.py` | Connect ke Google Sheets, CRUD operations, auto-create spreadsheet & sheets jika belum ada | 🔴 Critical |
| 1.6 | `services/parser.py` | Parse input format `+/-amount note`, extract amount & note | 🔴 Critical |
| 1.7 | `constants/categories.py` | Definisikan semua kategori + keywords + emoji | 🔴 Critical |
| 1.8 | `handlers/start.py` | `/start` welcome message, `/help` command | 🔴 Critical |
| 1.9 | `handlers/transaction.py` | Handle text message, parse, save ke Sheets, kirim konfirmasi | 🔴 Critical |
| 1.10 | `utils/formatter.py` | Format Rupiah (`Rp25.000`), format tanggal | 🟡 High |
| 1.11 | `utils/validator.py` | Validasi input: amount > 0, note not empty | 🟡 High |
| 1.12 | `utils/cache.py` | In-memory cache untuk saldo & recent transactions | 🟡 High |
| 1.13 | `bot.py` | Entry point, register handlers, start polling | 🔴 Critical |
| 1.14 | Smart detection | Detect input tanpa prefix, tampilkan inline keyboard konfirmasi | 🟢 Medium |

### Output Phase 1

```
✅ Bot Telegram aktif & merespons
✅ User ketik "-25000 makan" → data masuk Google Sheets
✅ User ketik "+5000000 gaji" → data masuk Google Sheets
✅ Smart detection dengan konfirmasi inline keyboard
✅ Auto-categorization berdasarkan keywords
✅ Format Rupiah benar
✅ Error handling untuk input tidak valid
```

### Acceptance Test

```bash
# Test 1: Bot merespons /start
User: /start
Bot: Welcome message ✅

# Test 2: Input pengeluaran
User: -25000 makan siang
Bot: ✅ Transaksi Tercatat! ... Saldo: Rp... ✅

# Test 3: Input pemasukan
User: +5000000 gaji
Bot: ✅ Transaksi Tercatat! ... Saldo: Rp... ✅

# Test 4: Data ada di Google Sheets
→ Buka spreadsheet, verifikasi row baru ✅

# Test 5: Invalid input
User: hello
Bot: ❌ Format tidak dikenali... ✅

# Test 6: Smart detection
User: bakso 25000
Bot: [Inline keyboard: Pengeluaran/Pemasukan/Batal] ✅
```

---

## Phase 2 — Reporting & Balance 📊

**Durasi:** 1-2 minggu
**Goal:** User bisa lihat saldo, laporan harian/mingguan/bulanan

### Tasks

| # | Task | Detail | Priority |
|---|------|--------|----------|
| 2.1 | `/saldo` | Hitung saldo dari semua transaksi, tampilkan summary | 🔴 Critical |
| 2.2 | `/today` | Filter transaksi hari ini, tampilkan list + total | 🔴 Critical |
| 2.3 | `/week` | Filter transaksi 7 hari terakhir, top categories, perbandingan vs minggu lalu | 🟡 High |
| 2.4 | `/month` | Filter transaksi bulan ini, cashflow, budget status | 🟡 High |
| 2.5 | `/hapus` & `/undo` | Hapus transaksi terakhir dengan konfirmasi | 🟡 High |
| 2.6 | Cache optimization | Cache saldo & recent data, invalidate saat ada transaksi baru | 🟡 High |
| 2.7 | Pagination | Jika transaksi > 10, tampilkan dengan inline keyboard pagination | 🟢 Medium |

### Output Phase 2

```
✅ /saldo menampilkan saldo + summary bulanan
✅ /today menampilkan transaksi hari ini
✅ /week menampilkan summary minggu + perbandingan
✅ /month menampilkan cashflow + top categories
✅ /hapus dan /undo berfungsi
✅ Data di-cache untuk performance
```

### Acceptance Test

```bash
# Test 1: Saldo akurat
→ Catat 3 transaksi, /saldo = jumlah benar ✅

# Test 2: Today filter benar
→ Catat transaksi, /today hanya tampilkan hari ini ✅

# Test 3: Week comparison
→ /week tampilkan perbandingan vs minggu lalu ✅

# Test 4: Undo works
→ /undo → transaksi terakhir terhapus, saldo terupdate ✅
```

---

## Phase 3 — Visualization, Budget & Receipt 📈

**Durasi:** 2-3 minggu
**Goal:** Chart, budget tracking, dan upload bukti transaksi

### Tasks

| # | Task | Detail | Priority |
|---|------|--------|----------|
| 3.1 | `services/charts.py` | Generate pie chart (kategori), bar chart (perbandingan), line chart (trend), cashflow chart | 🔴 Critical |
| 3.2 | `/chart` | Inline keyboard menu pilih jenis chart, generate & kirim PNG | 🔴 Critical |
| 3.3 | `services/budget.py` | Set budget per kategori, track usage, calculate percentage | 🟡 High |
| 3.4 | `/budget` | Set budget, lihat status budget, progress bar text | 🟡 High |
| 3.5 | Budget warning | Auto-send warning saat budget 80% dan 100% | 🟡 High |
| 3.6 | `services/drive.py` | Upload foto ke Google Drive, return shareable URL | 🟡 High |
| 3.7 | `handlers/receipt.py` | Handle foto, pilih transaksi, upload, link ke transaction | 🟡 High |
| 3.8 | Chart styling | Warna menarik, label jelas, dark theme friendly | 🟢 Medium |

### Output Phase 3

```
✅ /chart menampilkan menu pilihan grafik
✅ Pie chart pengeluaran per kategori
✅ Bar chart perbandingan kategori
✅ Line chart trend harian
✅ Cashflow chart income vs expense
✅ /budget set dan lihat budget
✅ Warning otomatis saat budget hampir habis
✅ Upload foto receipt → tersimpan di Google Drive
✅ Receipt terhubung ke transaksi
```

### Acceptance Test

```bash
# Test 1: Chart generation
→ /chart → pilih Pie → bot kirim gambar PNG ✅

# Test 2: Budget warning
→ Set budget Food 100000, catat -85000 makan → warning 80% ✅

# Test 3: Receipt upload
→ Kirim foto → pilih transaksi → link tersimpan di Sheets ✅
```

---

## Phase 4 — Automation, Polish & Deployment 🚀

**Durasi:** 1-2 minggu
**Goal:** Reminder, scheduled reports, export, deploy ke cloud

### Tasks

| # | Task | Detail | Priority |
|---|------|--------|----------|
| 4.1 | `services/scheduler.py` | Setup APScheduler untuk daily reminder & summary | 🔴 Critical |
| 4.2 | Daily reminder | 20:00 — reminder jika belum ada transaksi | 🟡 High |
| 4.3 | Daily summary | 21:00 — kirim ringkasan hari ini | 🟡 High |
| 4.4 | `/export` | Export transaksi ke CSV, kirim via Telegram file | 🟡 High |
| 4.5 | `/settings` | Ubah timezone, reminder time, currency | 🟢 Medium |
| 4.6 | Error handling polish | Retry logic, graceful degradation, user-friendly errors | 🟡 High |
| 4.7 | Rate limiting | Max 30 transaksi/menit per user | 🟢 Medium |
| 4.8 | Logging | Setup proper logging ke file, rotate logs | 🟢 Medium |
| 4.9 | Unit tests | Test parser, sheets service, budget logic | 🟡 High |
| 4.10 | Deploy ke cloud | Railway/Render/Oracle — setup webhook, env vars | 🔴 Critical |
| 4.11 | Documentation | README.md: setup guide, API keys, deployment | 🟡 High |
| 4.12 | Monthly summary | Awal bulan kirim summary bulan sebelumnya | 🟢 Medium |

### Output Phase 4

```
✅ Reminder harian berjalan otomatis
✅ Summary harian dikirim jam 21:00
✅ /export kirim file CSV
✅ /settings bisa ubah timezone & reminder
✅ Rate limiting aktif
✅ Proper logging
✅ Unit tests passing
✅ Bot deployed & running 24/7 di cloud
✅ README dokumentasi lengkap
```

### Acceptance Test

```bash
# Test 1: Reminder fires
→ Tunggu jam 20:00, tidak ada transaksi → bot kirim reminder ✅

# Test 2: Summary fires
→ Tunggu jam 21:00 → bot kirim summary ✅

# Test 3: Export
→ /export → bot kirim file .csv ✅

# Test 4: Deploy
→ Bot aktif 24/7 di cloud, restart otomatis ✅

# Test 5: Full flow
→ Catat 10 transaksi → /month → /chart pie → semua benar ✅
```

---

# 13. Deployment Strategy (Free)

| Platform | Free Tier | Pros | Cons |
|----------|-----------|------|------|
| **Railway** | 500 jam/bulan | Easy deploy, GitHub integration | Bisa habis jam |
| **Render** | 750 jam/bulan | Generous, auto-deploy | Cold start 30 detik |
| **Oracle Cloud** | Always free VM | Unlimited, full control | Setup lebih kompleks |
| **PythonAnywhere** | Always free | Python native | Limited features |

**Rekomendasi:** Mulai dengan **Railway** untuk development, migrasi ke **Oracle Cloud** untuk production (always free).

### Deployment Checklist

```
[ ] Environment variables configured
[ ] credentials.json uploaded secara aman
[ ] Webhook URL configured
[ ] Auto-restart enabled
[ ] Monitoring/health check active
[ ] Backup strategy documented
```

---

# 14. MVP Checklist

Bot dianggap MVP jika:

| # | Feature | Phase |
|---|---------|-------|
| ✅ | Bot Telegram aktif & merespons | 1 |
| ✅ | User bisa catat pengeluaran (`-25000 makan`) | 1 |
| ✅ | User bisa catat pemasukan (`+5000000 gaji`) | 1 |
| ✅ | Auto-categorization | 1 |
| ✅ | Data tersimpan di Google Sheets | 1 |
| ✅ | `/saldo` menampilkan saldo | 2 |
| ✅ | `/today` laporan hari ini | 2 |
| ✅ | `/month` laporan bulanan | 2 |
| ✅ | `/chart` kirim grafik | 3 |
| ✅ | Upload foto receipt | 3 |
| ✅ | Budget tracking | 3 |
| ✅ | Daily reminder | 4 |
| ✅ | Deployed 24/7 | 4 |

---

# 15. Future Roadmap (Post-MVP)

| Feature | Deskripsi | Estimasi |
|---------|-----------|----------|
| 🤖 OCR Receipt | Baca nominal dari foto struk (Tesseract/Google Vision) | Phase 5 |
| 🧠 AI Categorization | NLP untuk auto-detect kategori lebih akurat | Phase 5 |
| 🌐 Web Dashboard | Simple web view untuk data keuangan | Phase 6 |
| 👥 Multi-user | Support keluarga/pasangan shared budget | Phase 6 |
| 📊 Prediction | Prediksi saldo akhir bulan berdasarkan trend | Phase 7 |
| 💡 Savings Tips | Saran penghematan berdasarkan pola spending | Phase 7 |
| 🔄 Recurring Transaction | Auto-catat transaksi rutin (gaji, cicilan) | Phase 5 |
| 📱 Mini App | Telegram Mini App untuk dashboard interaktif | Phase 8 |

---

# End of PRD v2.0
