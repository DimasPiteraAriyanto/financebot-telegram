"""Message templates for FinanceBot responses."""

WELCOME_MESSAGE = """
👋 **Selamat datang di FinanceBot!**

Bot manajemen keuangan pribadi serba cepat & gratis.

**Cara Catat Transaksi:**
• Pengeluaran (pakai `-`): `-25000 makan siang`
• Pemasukan (pakai `+`): `+5000000 gaji juli`
• Tanpa prefix: `bakso 25000` (konfirmasi manual)

**Perintah yang Tersedia:**
/saldo - Lihat saldo saat ini
/today - Laporan hari ini
/week - Laporan minggu ini
/month - Laporan bulan ini
/chart - Grafik pengeluaran
/budget - Pengaturan budget
/undo - Batalkan transaksi terakhir
/help - Panduan penggunaan

Semua data tersimpan otomatis & aman di Google Sheets milikmu.
"""

HELP_MESSAGE = """
📖 **Panduan Penggunaan FinanceBot**

**1. Input Pengeluaran**
Contoh:
`-25000 makan siang`
`-15000 gojek ke kantor`
`-150000 belanja bulanan`

**2. Input Pemasukan**
Contoh:
`+5000000 gaji juli`
`+250000 project freelance`

**3. Format Cepat Tanpa Prefix**
Ketik: `nasi goreng 20000`
Bot akan menanyakan apakah ini pengeluaran atau pemasukan via tombol.

**4. Laporan & Saldo**
• `/saldo` - Cek saldo akhir
• `/today` - Rekap hari ini
• `/week` - Rekap 7 hari terakhir
• `/month` - Rekap bulan ini
"""

UNAUTHORIZED_MESSAGE = "⛔ Maaf, Anda tidak memiliki akses untuk menggunakan bot ini."

INVALID_FORMAT_MESSAGE = """
❌ **Format tidak dikenali**

Gunakan format:
• `-25000 makan siang` (Pengeluaran)
• `+5000000 gaji` (Pemasukan)
• `bakso 25000` (Smart Detection)

Ketik /help untuk bantuan lengkap.
"""

TRANSACTION_SUCCESS_MESSAGE = """
✅ **Transaksi Tercatat!**

📁 **Kategori**  : {emoji} {category}
💰 **Nominal**   : {amount_formatted}
📝 **Catatan**   : {note}
📅 **Tanggal**   : {datetime_formatted}

💳 **Saldo**     : {balance_formatted}
"""

SMART_DETECT_PROMPT = """
🔍 **Transaksi Terdeteksi**

📝 Catatan : {note}
💰 Nominal : {amount_formatted}
📁 Kategori: {emoji} {category}

Apakah ini **Pengeluaran** atau **Pemasukan**?
"""

TRANSACTION_DELETED_MESSAGE = "🗑️ Transaksi **{transaction_id}** ({amount_formatted}) berhasil dibatalkan."

NO_TRANSACTIONS_MESSAGE = "ℹ️ Belum ada transaksi yang tercatat."
