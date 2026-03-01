import os
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, CallbackQueryHandler
)
from telegram import Update
from handlers.start import start, help_command
from handlers.calculator import calculator, handle_calculation
from handlers.recipe_fixed import search_recipe_indonesia, recipe_detail_callback
from handlers.translate import translate
from handlers.weather import weather
from handlers.prayer_advanced import prayer_advanced, set_location, my_location

TOKEN = os.environ.get("TOKEN")

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("kalkulator", calculator))
    application.add_handler(CommandHandler("resep", search_recipe_indonesia))
    application.add_handler(CommandHandler("translate", translate))
    application.add_handler(CommandHandler("cuaca", weather))
    application.add_handler(CommandHandler("shalat", prayer_advanced))
    application.add_handler(CommandHandler("setlokasi", set_location))
    application.add_handler(CommandHandler("mylokasi", my_location))  # <-- GANTI INI!
    
    # Message handler untuk kalkulator
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Regex(r'^[\d\s\+\-\*\/\(\)\.]+$'), 
        handle_calculation
    ))
    
    # Callback handler untuk resep
    application.add_handler(CallbackQueryHandler(recipe_detail_callback, pattern="^recipe_"))
    
    print("Bot started with advanced features & database...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
