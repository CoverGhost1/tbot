import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update
from handlers.start import start, help_command
from handlers.calculator import calculator, handle_calculation
from handlers.recipe import search_recipe, recipe_callback
from handlers.translate import translate  # UBAH: Hapus handle_translation
from handlers.weather import weather
from handlers.prayer import prayer

TOKEN = os.environ.get("TOKEN", "YOUR_BOT_TOKEN")

def main():
    # Buat aplikasi bot
    application = Application.builder().token(TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("kalkulator", calculator))
    application.add_handler(CommandHandler("resep", search_recipe))
    application.add_handler(CommandHandler("translate", translate))
    application.add_handler(CommandHandler("cuaca", weather))
    application.add_handler(CommandHandler("shalat", prayer))
    
    # Message handler untuk kalkulator (tangkep pesan angka & operator)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Regex(r'^[\d\s\+\-\*\/\(\)\.]+$'), 
        handle_calculation
    ))
    
    # Callback query handler untuk inline buttons (resep)
    application.add_handler(CallbackQueryHandler(recipe_callback))
    
    # Jalankan bot
    print("Bot started...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
