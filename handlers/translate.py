from googletrans import Translator
from telegram import Update
from telegram.ext import ContextTypes

# Inisialisasi translator
translator = Translator()

# Daftar kode bahasa umum
LANGUAGE_CODES = {
    'id': 'Indonesia',
    'en': 'Inggris',
    'ar': 'Arab',
    'ja': 'Jepang',
    'ko': 'Korea',
    'zh-cn': 'Mandarin (China)',
    'es': 'Spanyol',
    'fr': 'Perancis',
    'de': 'Jerman',
    'ru': 'Rusia',
    'hi': 'Hindi',
    'nl': 'Belanda',
    'pt': 'Portugis',
    'it': 'Italia',
    'th': 'Thailand',
    'vi': 'Vietnam'
}

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Terjemahkan teks ke bahasa lain"""
    if len(context.args) < 2:
        # Tampilkan panduan
        codes_list = "\n".join([f"• `{code}`: {name}" for code, name in list(LANGUAGE_CODES.items())[:10]])
        await update.message.reply_text(
            "🌍 **Terjemahan Bahasa**\n\n"
            "Format: `/translate <kode> <teks>`\n"
            "Contoh: `/translate id hello world`\n\n"
            "**Kode bahasa umum:**\n"
            f"{codes_list}\n\n"
            "📝 *Ketik `/translate` untuk info lebih lengkap*",
            parse_mode='Markdown'
        )
        return
    
    dest_lang = context.args[0].lower()
    text = " ".join(context.args[1:])
    
    # Validasi kode bahasa
    if dest_lang not in LANGUAGE_CODES:
        await update.message.reply_text(
            f"❌ Kode bahasa '{dest_lang}' tidak valid.\n"
            f"Coba kode: id, en, ar, ja, ko, zh-cn"
        )
        return
    
    try:
        # Deteksi bahasa asal
        detected = translator.detect(text)
        source_lang = detected.lang
        
        # Terjemahkan
        result = translator.translate(text, dest=dest_lang)
        
        # Format pesan
        source_name = LANGUAGE_CODES.get(source_lang, source_lang)
        dest_name = LANGUAGE_CODES.get(dest_lang, dest_lang)
        
        translation_msg = (
            f"🌍 **Terjemahan**\n"
            f"Dari: {source_name} ({source_lang})\n"
            f"Ke: {dest_name} ({dest_lang})\n\n"
            f"**Asli:**\n{text}\n\n"
            f"**Hasil:**\n{result.text}"
        )
        
        await update.message.reply_text(translation_msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal menerjemahkan. Error: {str(e)}")
