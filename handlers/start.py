from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_msg = (
        f"Halo {user.first_name}! 👋\n\n"
        "Saya bot multifungsi dengan fitur:\n\n"
        "🔢 `/kalkulator` - Kalkulator sederhana\n"
        "   Contoh: Ketik `2 + 2 * 3` langsung di chat\n\n"
        "🍳 `/resep <nama masakan>` - Cari resep masakan\n"
        "   Contoh: `/resep nasi goreng`\n\n"
        "🌍 `/translate <kode> <teks>` - Terjemahan bahasa\n"
        "   Contoh: `/translate id hello world`\n"
        "   Kode bahasa: id (Indonesia), en (Inggris), ar (Arab), dll\n\n"
        "☁️ `/cuaca <kota>` - Info cuaca terkini\n"
        "   Contoh: `/cuaca Jakarta`\n\n"
        "🕌 `/shalat <kota>` - Jadwal shalat hari ini\n"
        "   Contoh: `/shalat Bandung`\n\n"
        "❓ `/help` - Tampilkan bantuan ini"
    )
    await update.message.reply_text(welcome_msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)  # Reuse start message
