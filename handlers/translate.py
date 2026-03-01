from deep_translator import GoogleTranslator
from telegram import Update
from telegram.ext import ContextTypes

LANGUAGE_CODES = {
    'id': 'Indonesia', 'en': 'Inggris', 'ar': 'Arab', 'ja': 'Jepang',
    'ko': 'Korea', 'zh-cn': 'Mandarin', 'es': 'Spanyol', 'fr': 'Perancis',
    'de': 'Jerman', 'ru': 'Rusia', 'hi': 'Hindi', 'nl': 'Belanda',
    'pt': 'Portugis', 'it': 'Italia', 'th': 'Thailand', 'vi': 'Vietnam'
}

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        codes_list = "\n".join([f"• `{code}`: {name}" for code, name in list(LANGUAGE_CODES.items())[:10]])
        await update.message.reply_text(
            "🌍 **Terjemahan Bahasa**\n\n"
            "Format: `/translate <kode> <teks>`\n"
            "Contoh: `/translate id hello world`\n\n"
            "**Kode bahasa umum:**\n"
            f"{codes_list}",
            parse_mode='Markdown'
        )
        return
    
    dest_lang = context.args[0].lower()
    text = " ".join(context.args[1:])
    
    if dest_lang not in LANGUAGE_CODES:
        await update.message.reply_text("❌ Kode bahasa tidak valid. Coba: id, en, ar, ja, ko, zh-cn")
        return
    
    try:
        translator = GoogleTranslator(source='auto', target=dest_lang)
        translated = translator.translate(text)
        
        await update.message.reply_text(
            f"🌍 **Terjemahan**\n"
            f"Ke: {LANGUAGE_CODES[dest_lang]} ({dest_lang})\n\n"
            f"**Hasil:**\n{translated}",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
